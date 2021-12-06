import datetime
import json

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from home_application.celery_task import (
    send_evaluate_daily,
    send_good_daily,
    send_unfinished_dairy,
)
from home_application.models import Daily, Group, GroupUser, OffDay, User
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
    date = json.loads(request.body).get("date")
    # 组内成员
    group_user_ids = GroupUser.objects.filter(group_id=group_id).values_list("user_id", flat=True)
    group_users = User.objects.filter(id__in=group_user_ids).values_list("username", flat=True)
    # 填写日报信息
    report_user_usernames = Daily.objects.filter(create_by__in=group_users, date=date).values_list(
        "create_by", flat=True
    )
    non_report_users = set(group_users) - set(report_user_usernames)
    username_str = ",".join(non_report_users)
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
        return JsonResponse({"result": False, "code": 0, "message": "评价不存在", "data": []})


@require_http_methods(["POST"])
@is_group_member(admin_needed=["POST"])
def update_evaluate_daily(request, group_id, daily_id):
    """
    修改日报的指定评论
    """
    try:
        daily = Daily.objects.get(id=daily_id)
    except Daily.DoesNotExist:
        return JsonResponse({"result": False, "code": 0, "message": "无此日报", "data": []})
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
    daily_ids = json.loads(request.body).get("daily_ids")
    date = Daily.objects.get(id=daily_ids[0]).date
    # 标记 是否找到该管理员的评价
    sign = True
    # 日报信息列表
    daily_list = []
    dailys = Daily.objects.filter(id__in=daily_ids)
    for daily in dailys:
        daily = daily.to_json()
        for evaluate in daily["evaluate"]:
            if evaluate["name"] == request.user.username:
                daily["evaluate"] = evaluate["evaluate"]
                sign = False
                break
        if sign:
            daily["evaluate"] = "管理员未评价"
        daily_list.append(daily)
    #  组内所有人
    user_id = GroupUser.objects.filter(group_id=group_id).values_list("user_id", flat=True)
    all_username = User.objects.filter(id__in=user_id).values_list("username", flat=True)
    if all_username:
        # 放进celery里
        all_username = ",".join([user for user in all_username])
        send_good_daily(request.user.username, all_username, date, daily_list)
        return JsonResponse({"result": True, "code": 0, "message": "发送成功", "data": []})
    else:
        return JsonResponse({"result": False, "code": 0, "message": "这个组没有成员", "data": []})


@require_http_methods(["POST"])
@is_group_member()
def add_off_info(request):
    """
    请假
    """
    req = json.loads(request.body)
    start_date = req.get("start_date")
    end_date = req.get("end_date")
    reason = req.get("reason")
    # 判断是否已请假
    username_list = [request.user.username]
    if not check_off_status(username_list, start_date):
        OffDay.objects.create(start_date=start_date, end_date=end_date, reason=reason, user=request.user.username)
        return JsonResponse({"result": True, "code": 0, "message": "请假成功", "data": []})
    else:
        return JsonResponse({"result": False, "code": 0, "message": "休假日期重叠", "data": []})


def check_off_status(username_list, date):
    """
    返回所有请假的人
    :param username_list: username 数组
    :param date: 日期字符串
    """
    # 直接筛选出请假记录，有请假记录即为请假的人
    # 请假开始时间在日期之前，结束时间在日期之后 start <= date <= end
    return OffDay.objects.filter(start_date__lte=date, end_date__gte=date, user__in=username_list).values_list(
        "user", flat=True
    )


@require_http_methods(["DELETE"])
@is_group_member()
def remove_off(request, group_id, offday_id):
    """
    撤回请假条
    不能撤回之前的
    主要作用与请假错误想撤回
    """
    try:
        OffDay.objects.get(id=offday_id).delete()
        return JsonResponse({"result": True, "code": 0, "message": "撤回成功", "data": []})
    except offday_id:
        return JsonResponse({"result": False, "code": 0, "message": "你没有请假", "data": []})
    
    
@require_http_methods(["GET"])
@is_group_member()
def display_personnel_information(request, group_id):
    """
    展示未请假人和请假人
    param sign：标记 1 返回未请假人 或 0返回请假人
    """
    date = request.GET.get("date")
    sign = request.GET.get("sign")
    # 组内所有人
    user_id = GroupUser.objects.filter(group_id=group_id).values_list("user_id", flat=True)
    username_list = User.objects.filter(id__in=user_id).values_list("username", flat=True)
    # 这个时间段所有请假的人
    off_day_list = check_off_status(username_list, date)
    if sign == 1:
        # 展示对应组对应日期未请假的人
        list_at_work_user = []
        list_work_user = set(username_list) - set(off_day_list)
        list_work_user = User.objects.filter(username__in=list_work_user).values()
        for list_work_user_sign in list_work_user:
            list_at_work_user.append(dict(list_work_user_sign))
        if list_at_work_user:
            return JsonResponse({"result": True, "code": 0, "message": "", "list_at_work_user": list_at_work_user})
        else:
            return JsonResponse({"result": True, "code": 0, "message": "所有人都已请假", "data": []})
    else:
        # 这个时间段所有请假的人
        off_day_list_return = []
        off_day_dict = OffDay.objects.filter(start_date__lte=date, end_date__gte=date, user__in=username_list).values()
        for off_day_dict in off_day_dict:
            off_day_dict["name"] = User.objects.filter(username=off_day_dict["user"]).values("name")[0]["name"]
            off_day_list_return.append(off_day_dict)
        if off_day_list_return:
            data = {
                "off_day_list_return": off_day_list_return,  # 请假人信息
            }
            return JsonResponse({"result": True, "code": 0, "message": "", "data": data})
        else:
            return JsonResponse({"result": False, "code": 0, "message": "今天没有请假的人", "data": []})
