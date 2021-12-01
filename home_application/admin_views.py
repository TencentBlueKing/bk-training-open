import datetime
import json

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from home_application.celery_task import (
    send_evaluate_daily,
    send_good_daily,
    send_unfinished_dairy,
)
from home_application.models import Daily, Group, GroupUser, User
from home_application.utils.decorator import is_group_member


@require_http_methods(["GET"])
def list_admin_group(request):
    """
    获取有权限管理的所有组
    """
    username = request.user.username
    groups = Group.objects.all()
    admin_group = []
    for group in groups:
        if username in group.admin_list:
            admin_group.append(group.to_json())
    return JsonResponse({"result": True, "code": 0, "manage": "", "data": admin_group})


@require_http_methods(["GET"])
@is_group_member(admin_needed=["GET"])
def list_member_daily(request, group_id):
    """
    获取成员的日报信息
    """
    today = datetime.datetime.now().date()
    date = request.GET.get("date", today)
    # 组内成员
    group_members = GroupUser.objects.filter(group_id=group_id)
    users = User.objects.filter(id__in=group_members.values_list("user_id", flat=True))
    # 日报信息
    dailies = Daily.objects.filter(date=date, create_by__in=users.values_list("username", flat=True))
    # 拼接响应
    data = []
    for user in users:
        try:
            daily = dailies.get(create_by=user.username).to_json()
            daily["write_status"] = True
        except Daily.DoesNotExist:
            daily = Daily(date=date, create_by=user.username, create_name=user.name, content="{}").to_json()
            daily["write_status"] = False
        data.append(daily)
    return JsonResponse({"result": True, "code": 0, "message": "", "data": data})


@require_http_methods(["POST"])
def evaluate_daily(request):
    """
    评价组员日报
    """
    req = json.loads(request.body)
    daily_id = req.get("daily_id")
    evaluate_content = req.get("evaluate")
    try:
        evaluate = Daily.objects.get(id=daily_id).evaluate
    except Daily.DoesNotExist:
        return JsonResponse({"result": False, "code": 1, "message": "日报不存在"})
    evaluate.append({"name": request.user.username, "evaluate": evaluate_content})
    Daily.objects.filter(id=daily_id).update(evaluate=evaluate)
    send_evaluate_daily(daily_id, evaluate_content)
    return JsonResponse({"result": True, "code": 0, "message": "点评成功", "data": []})


@require_http_methods(["POST"])
@is_group_member(admin_needed=["POST"])
def notice_non_report_users(request, group_id):
    """
    提醒未写日报成员写日报
    """
    date = request.GET.get("date")
    # 组内成员
    group_user_ids = GroupUser.objects.filter(group_id=group_id).values_list("user_id", flat=True)
    group_users = User.objects.filter(id__in=group_user_ids).values_list("username", flat=True)
    # 填写日报信息
    report_user_usernames = Daily.objects.filter(create_by__in=group_users, date=date).values_list(
        "create_by", flat=True
    )
    non_report_users = set(group_users) - set(report_user_usernames)
    username_str = ",".join([user for user in non_report_users])
    # 发送邮件
    if non_report_users:
        # 放进celery里
        send_unfinished_dairy.delay(username_str, date)
        return JsonResponse({"result": True, "code": 0, "message": "一键提醒成功", "data": []})

    else:
        return JsonResponse({"result": True, "code": 0, "message": "无未写日报成员", "data": []})


@require_http_methods(["DELETE"])
@is_group_member(admin_needed=["DELETE"])
def delete_evaluate_daily(request, group_id, daily_id):
    """
    删除日报中评价
    仅可以删除自己的
    """
    username = request.user.username
    daily = Daily.objects.get(id=daily_id)
    if daily.remove_evaluate(username):
        return JsonResponse({"result": True, "code": 0, "message": "删除成功", "data": []})
    else:
        return JsonResponse({"result": False, "code": 0, "message": "评价不存在成功", "data": []})


@require_http_methods(["POST"])
@is_group_member(admin_needed=["POST"])
def update_evaluate_daily(request, group_id, daily_id):
    """
    修改日报的指定评论
    """
    try:
        daily = Daily.objects.get(id=daily_id)
    except Daily.DoesNotExist:
        return JsonResponse({"result": False, "code": 0, "message": "无此评论", "data": []})
    evaluate_content = request.GET.get("evaluate_content")
    username = request.user.username
    daily.add_evaluate(username, evaluate_content)
    return JsonResponse({"result": True, "code": 0, "message": "修改成功", "data": []})


@require_http_methods(["POST"])
@is_group_member(admin_needed=["POST"])
def send_evaluate_all(request, group_id):
    """
    发生邮件给所有组成员
    可以发生多个邮件
    """
    daily_ids = request.GET.get("daily_ids")
    date = Daily.objects.filter(id=daily_ids[0]).values_list("date")
    date = str(date[0])
    username = request.user.username
    evaluate_name = []
    # 日报内容 评价
    content_list = Daily.objects.filter(id__in=daily_ids).values_list("content", flat=True)
    evaluate_list = Daily.objects.filter(id__in=daily_ids).values_list("evaluate", flat=True)
    # 找到目前管理员写的评价
    for evaluate in evaluate_list:
        for evaluate in evaluate:
            if evaluate["name"] == username:
                evaluate_name.append(evaluate)
    # 所有成员
    user_id = GroupUser.objects.filter(group_id=group_id).values_list("user_id", flat=True)
    all_username = User.objects.filter(id__in=user_id).values_list("username", flat=True)
    if all_username:
        # 放进celery里
        all_username = ",".join([user for user in all_username])
        send_good_daily.delay(all_username, date, content_list, evaluate_name)
        return JsonResponse({"result": True, "code": 0, "message": "发送成功", "data": []})
    else:
        return JsonResponse({"result": True, "code": 0, "message": "这个组没有成员", "data": []})
