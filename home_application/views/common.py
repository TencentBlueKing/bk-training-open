import math

from django.http import JsonResponse

# 开发框架中通过中间件默认是需要登录态的，如有不需要登录的，可添加装饰器login_exempt
# 装饰器引入 from blueapps.account.decorators import login_exempt
from django.shortcuts import render

from blueking.component.shortcuts import get_client_by_request


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
