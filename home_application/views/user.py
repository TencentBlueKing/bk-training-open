from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from home_application.models import User
from home_application.utils.tools import check_user_is_admin

# 开发框架中通过中间件默认是需要登录态的，如有不需要登录的，可添加装饰器login_exempt
# 装饰器引入 from blueapps.account.decorators import login_exempt


def get_user(request):
    """获取当前用户信息"""
    user = User.objects.get(id=request.user.id)
    data = {"id": user.id, "username": user.username, "name": user.name, "phone": user.phone, "email": user.email}
    return JsonResponse({"result": True, "code": 0, "message": "查询成功", "data": data})


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
