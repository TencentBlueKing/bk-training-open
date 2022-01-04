import datetime
import json

from django.forms import model_to_dict
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from home_application.models import GroupUser, OffDay, User
from home_application.utils.decorator import is_group_member


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
