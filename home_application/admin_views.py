import datetime
import json

from django.forms import model_to_dict
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from home_application.celery_task import send_evaluate_daily, send_good_daily
from home_application.models import Daily, Group, GroupUser, OffDay, User
from home_application.utils.decorator import is_group_member
from home_application.utils.mail_operation import remind_to_write_daily


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
            daily = Daily(date=date, create_by=user.username, create_name=user.name, content=[]).to_json()
            daily["write_status"] = False
        data.append(daily)
    return JsonResponse({"result": True, "code": 0, "message": "", "data": data})


@require_http_methods(["GET"])
@is_group_member(admin_needed=["GET"])
def list_group_admin(request, group_id):
    """
    获取组内管理员列表
    """
    # 组内成员
    try:
        admins = Group.objects.get(id=group_id).admin_list
    except Group.DoesNotExist:
        return JsonResponse({"result": False, "code": 1, "message": "组不存在", "data": []})
    return JsonResponse({"result": True, "code": 0, "message": "", "data": admins})


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
    # 获取发邮件人的姓名
    evaluate_name = User.objects.get(username=request.user.username)
    send_evaluate_daily.apply_async(
        kwargs={"evaluate_name": evaluate_name.name, "daily_id": daily_id, "evaluate_content": evaluate_content}
    )
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
    # 管理员不用写日报
    admin_list = Group.objects.get(id=group_id).admin_list
    non_report_users = set(group_users) - set(report_user_usernames) - set(admin_list)
    # 请假的人不用写日报
    off_day_list = OffDay.objects.filter(start_date__lte=date, end_date__gte=date, user__in=non_report_users)
    non_report_users = set(non_report_users) - set(off_day_list)
    # 发送邮件
    if non_report_users:
        remind_to_write_daily.apply_async(kwargs={"username_list": list(non_report_users), "date": date})
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
    evaluate_content = json.loads(request.body).get("evaluate_content")
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
        sign = True
    #  组内所有人
    user_id = GroupUser.objects.filter(group_id=group_id).values_list("user_id", flat=True)
    all_username = User.objects.filter(id__in=user_id).values_list("username", flat=True)
    # 排除管理员
    admin_list = Group.objects.get(id=group_id).admin_list
    all_username = set(all_username) - set(admin_list)
    evaluate_name = User.objects.get(username=request.user.username)
    if all_username:
        # 放进celery里
        all_username = ",".join(all_username)
        send_good_daily.apply_async(
            kwargs={
                "evaluate_name": evaluate_name.name,
                "user_name": all_username,
                "date": date,
                "daily_list": daily_list,
            }
        )
        return JsonResponse({"result": True, "code": 0, "message": "发送成功", "data": []})
    else:
        return JsonResponse({"result": False, "code": 0, "message": "这个组没有成员", "data": []})


@require_http_methods(["POST"])
def add_off_info(request):
    """
    请假
    """
    req = json.loads(request.body)
    start_date = req.get("start_date")
    end_date = req.get("end_date")
    reason = req.get("reason")
    # 判断是否已请假
    has_off = OffDay.objects.filter(start_date__lte=start_date, end_date__gte=start_date, user=request.user.username)
    if not has_off.exists():
        OffDay.objects.create(start_date=start_date, end_date=end_date, reason=reason, user=request.user.username)
        return JsonResponse({"result": True, "code": 0, "message": "请假成功", "data": []})
    else:
        return JsonResponse({"result": False, "code": 0, "message": "休假日期重叠", "data": []})


@require_http_methods(["DELETE"])
@is_group_member()
def remove_off(request, group_id, offday_id):
    """
    撤回请假条
    不能撤回之前的e
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
    param sign：标记 2 返回当前用户今天之后的所有请假时间 1 返回未请假人 或 0返回请假人
    """
    sign = request.GET.get("sign")
    if sign == "2":
        data = list(
            OffDay.objects.filter(end_date__gte=datetime.datetime.now(), user=request.user.username).values_list(
                "start_date", "end_date"
            )
        )
        return JsonResponse({"result": True, "code": 0, "message": "", "data": data})
    date = request.GET.get("date")
    # 组内所有人
    user_ids = GroupUser.objects.filter(group_id=group_id).values_list("user_id", flat=True)
    users = User.objects.filter(id__in=user_ids)
    # 请假的人
    off_day_list = OffDay.objects.filter(end_date__gte=date, user__in=users.values_list("username", flat=True))
    # 这个时间段所有请假的人
    off_day_now_list = OffDay.objects.filter(
        start_date__lte=date, end_date__gte=date, user__in=users.values_list("username", flat=True)
    )
    data = []
    # 展示对应组对应日期请假的人
    if sign == "0":
        off_infos = {info.id: model_to_dict(info) for info in off_day_list}
        users = users.filter(username__in=off_day_list.values_list("user", flat=True))
        for user in users:
            for key, value in off_infos.items():
                if off_infos[key]["user"] == user.username:
                    user_data = model_to_dict(user)
                    user_data.update({"off_info": off_infos.get(key)})
                    data.append(user_data)
    # 展示对应组对应日期未请假的人
    elif sign == "1":
        at_work_usernames = set(users.values_list("username", flat=True)) - set(
            off_day_now_list.values_list("user", flat=True)
        )
        data = [model_to_dict(user) for user in users.filter(username__in=at_work_usernames)]
    return JsonResponse({"result": True, "code": 0, "message": "", "data": data})
