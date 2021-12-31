import json

from django.db import IntegrityError
from django.http import JsonResponse
from django.utils.datetime_safe import datetime
from django.views.decorators.http import require_http_methods

from home_application.models import User
from home_application.utils.tools import check_user_is_admin

# 开发框架中通过中间件默认是需要登录态的，如有不需要登录的，可添加装饰器login_exempt
# 装饰器引入 from blueapps.account.decorators import login_exempt


def get_user(request):
    """获取当前用户信息"""
    try:
        user = User.objects.get(id=request.user.id)
        data = {"id": user.id, "username": user.username, "name": user.name, "phone": user.phone, "email": user.email}
    except User.DoesNotExist:
        data = {"id": request.user.id, "username": request.user.username}
    return JsonResponse({"result": True, "code": 0, "message": "查询成功", "data": data})


def update_user(request):
    """更改用户信息"""
    req = json.loads(request.body)
    name = req.get("display_name")
    phone = req.get("phone")
    email = req.get("email")
    try:
        User.objects.filter(id=request.user.id).update(name=name, phone=phone, email=email, update_time=datetime.now())
    except IntegrityError:
        return JsonResponse({"result": False, "code": 1, "message": "更新失败，用户名已存在"})
    else:
        return JsonResponse({"result": True, "code": 0, "message": "更新成功", "data": []})


def auto_sign_users(usernames: list, user_infos: list):
    """
    注册不存在的用户信息
    :param usernames: 用户名数组
    :param user_infos: 用户信息数组
    """
    exist_users = User.objects.filter(username__in=usernames).values_list("username", flat=True)
    user_list = []
    for user in user_infos:
        username = user.get("username")
        if username not in exist_users:
            user_list.append(
                User(
                    id=user.get("id"),
                    username=user.get("username"),
                    name=user.get("display_name"),
                    phone=user.get("phone"),
                    email=user.get("email"),
                )
            )
    User.objects.bulk_create(user_list, ignore_conflicts=True)


@require_http_methods(["GET"])
def check_user_admin(request):
    user_is_admin = check_user_is_admin(request, 1)
    return JsonResponse({"result": user_is_admin, "code": 200, "message": "", "data": []})
