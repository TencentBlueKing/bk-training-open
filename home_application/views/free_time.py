import datetime
import json

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_http_methods

from home_application.models import FreeTime, Group, GroupUser, User
from home_application.utils.decorator import is_group_member

# 开发框架中通过中间件默认是需要登录态的，如有不需要登录的，可添加装饰器login_exempt
# 装饰器引入 from blueapps.account.decorators import login_exempt


@require_http_methods(["GET", "POST"])
def free_time_get_post(request):
    """空闲时间的增删改查"""
    # 查
    if request.method == "GET":
        # 要查询空闲时间的起止日期
        start_date = request.GET.get("start_date", "")
        end_date = request.GET.get("end_date", "")
        try:
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
            if start_date > end_date:
                return JsonResponse({"result": False, "code": 1, "message": "结束日期不得早于起始日期", "data": []})
        except ValueError:
            return JsonResponse({"result": False, "code": 1, "message": "日期格式错误", "data": []})
        res_data = FreeTime.objects.get_free_time([request.user.username], start_date, end_date)[0]["free_time"]
        return JsonResponse({"result": True, "code": 0, "message": "", "data": res_data})
    # 增
    if request.method == "POST":
        req = json.loads(request.body)
        try:
            # 核验参数
            free_times = req["free_times"]
            if not isinstance(free_times, list):
                return JsonResponse({"result": False, "code": 1, "message": "参数格式错误，缺少free_times", "data": []})
            for f_time in free_times:
                f_time["start_time"] = datetime.datetime.strptime(f_time["start_time"], "%Y-%m-%d %H:%M")
                f_time["end_time"] = datetime.datetime.strptime(f_time["end_time"], "%Y-%m-%d %H:%M")

            # 新增数据，添加成功则无返回值，为None，失败则返回失败的详细信息（字符串）
            add_status, add_msg = FreeTime.objects.add_free_time(request.user.username, free_times)
            if not add_status:
                return JsonResponse({"result": False, "code": 2, "message": add_msg, "data": []})
            else:
                return JsonResponse({"result": True, "code": 0, "message": "添加空闲时间成功", "data": []})
        except ValueError:
            return JsonResponse({"result": False, "code": 1, "message": "时间格式错误", "data": []})
        except KeyError:
            return JsonResponse({"result": False, "code": 1, "message": "参数格式错误，缺少start_time或end_time", "data": []})


@require_http_methods(["PATCH", "DELETE"])
def free_time_patch_delete(request, free_time_id):
    # 改
    if request.method == "PATCH":
        req = json.loads(request.body)
        new_start_time = req.get("new_start_date", "")
        new_end_time = req.get("new_end_date", "")
        try:
            free_time_obj = FreeTime.objects.get(id=free_time_id)
            free_time_obj.start_time = datetime.datetime.strptime(new_start_time, "%Y-%m-%d %H:%M")
            free_time_obj.end_time = datetime.datetime.strptime(new_end_time, "%Y-%m-%d %H:%M")
            save_status, save_msg = free_time_obj.save()
            # 保存出错则直接返回出错原因
            if not save_status:
                return JsonResponse({"result": False, "code": 2, "message": save_msg, "data": []})
            return JsonResponse({"result": True, "code": 0, "message": "修改成功", "data": []})
        except FreeTime.DoesNotExist:
            return JsonResponse({"result": False, "code": 2, "message": "修改失败，未找到对应的空闲时间", "data": []})
        except ValueError:
            return JsonResponse({"result": False, "code": 1, "message": "修改失败，时间格式错误", "data": []})
    # 删
    if request.method == "DELETE":
        try:
            FreeTime.objects.get(id=free_time_id, username=request.user.username).delete()
            return JsonResponse({"result": True, "code": 0, "message": "删除成功", "data": []})
        except FreeTime.DoesNotExist:
            return JsonResponse({"result": False, "code": 1, "message": "删除失败，未找到对应的空闲时间", "data": []})


@require_GET
@is_group_member()
def group_free_time(request, group_id):
    # 要查询空闲时间的起止日期
    try:
        start_date = request.GET.get("start_date", "")
        end_date = request.GET.get("end_date", "")
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
        if start_date > end_date:
            return JsonResponse({"result": False, "code": 1, "message": "结束日期不得早于起始日期", "data": []})
    except ValueError:
        return JsonResponse({"result": False, "code": 1, "message": "日期格式错误", "data": []})
    user_ids = GroupUser.objects.filter(group_id=group_id).values_list("user_id", flat=True)
    usernames = User.objects.filter(id__in=user_ids).values_list("username", flat=True)
    admin_list = Group.objects.get(id=group_id).admin_list
    usernames = list(set(usernames) - set(admin_list))
    free_times = FreeTime.objects.get_free_time(usernames, start_date, end_date)
    return JsonResponse({"result": True, "code": 0, "message": "", "data": free_times})


@require_GET
def user_free_time(request):
    # 查找用户所有空闲时间
    username = request.GET.get("username")
    res_data = []
    weekday = datetime.datetime.now().weekday()
    # 周六周天展示下周时间
    if weekday >= 5:
        if weekday == 5:
            weekday = -2
        else:
            weekday = -1
    res_data_list = FreeTime.objects.get_free_time(
        [username],
        datetime.date.today() + datetime.timedelta(days=-weekday),
        datetime.date.today() + datetime.timedelta(days=-weekday + 4),
    )[0]["free_time"]
    weekStr = ["一", "二", "三", "四", "五"]
    for index in range(0, 5):
        date = datetime.date.today() + datetime.timedelta(days=-weekday + index)
        is_day = False
        if weekday == index:
            is_day = True
        res_data.append(
            {
                "date": date,
                "weekend": "星期" + weekStr[index],
                "is_day": is_day,
                "free_time": [
                    {
                        "start_time": f_time["start_time"],
                        "end_time": f_time["end_time"],
                    }
                    for f_time in res_data_list
                    if f_time["date"] == date
                ],
            }
        )
    return JsonResponse({"result": True, "code": 0, "message": "", "data": res_data})
