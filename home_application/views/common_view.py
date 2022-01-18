import datetime
import math

from django.http import JsonResponse

# 开发框架中通过中间件默认是需要登录态的，如有不需要登录的，可添加装饰器login_exempt
# 装饰器引入 from blueapps.account.decorators import login_exempt
from django.shortcuts import render
from django.views.decorators.http import require_GET

from blueking.component.shortcuts import get_client_by_request
from home_application.utils.calendar_util import CalendarHandler, get_holidays_in_range


def home(request):
    """
    首页
    """
    return render(request, "index.html")


def get_all_bk_users(request):
    """从蓝鲸平台，拉取所有用户列表"""
    client = get_client_by_request(request=request)
    response = client.usermanage.list_users(fields="id,username,display_name,email,telephone", page=1, pageSize=50)
    result = response.get("result")
    if result:
        count = response.get("data").get("count")
        total_page = math.ceil(count / 50)
        data = response.get("data").get("results")
        for page in range(2, total_page + 1):
            response = client.usermanage.list_users(
                fields="id,username,display_name,email,telephone", page=page, pageSize=50
            )
            result = response.get("result")
            if result:
                data.extend(response.get("data").get("results"))
            else:
                return response
        return JsonResponse(
            {"result": True, "code": 0, "data": {"count": count, "results": data}, "message": "获取蓝鲸用户列表成功"}
        )
    else:
        # 请求接口成功，但获取内容失败，返回错误信息
        return response


@require_GET
def get_workday_info(request):
    """获取指定日期是否为节假日以及他的上一个工作日"""
    date = request.GET.get("date", "")
    try:
        date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({"result": False, "code": 1, "message": "日期格式错误", "data": []})
    date_info = CalendarHandler(date)
    return JsonResponse(
        {
            "result": True,
            "code": 0,
            "message": "success",
            "data": {
                "is_holiday": date_info.is_holiday,
                "note": date_info.note,
                "last_workday": date_info.last_workday,
            },
        }
    )


@require_GET
def get_holidays(request):
    """获取一个时间段内的节假日信息（不含普通周末）"""
    start_date = request.GET.get("start_date", "")
    end_date = request.GET.get("end_date", "")
    try:
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({"result": False, "code": 1, "message": "日期格式错误", "data": []})

    if start_date > end_date:
        return JsonResponse({"result": False, "code": 1, "message": "起始日期不得晚于结束日期", "data": []})

    return JsonResponse(
        {"result": True, "code": 0, "message": "success", "data": get_holidays_in_range(start_date, end_date)}
    )
