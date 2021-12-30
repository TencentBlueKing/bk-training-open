import json

from django.db import IntegrityError
from django.http import JsonResponse
from django.utils.datetime_safe import datetime
from django.views.decorators.http import require_GET, require_http_methods

from blueking.component.shortcuts import get_client_by_request
from home_application.models import Daily, GroupUser, User
from home_application.utils.calendar_util import CalendarHandler
from home_application.utils.decorator import is_group_member
from home_application.utils.report_operation import content_format_as_json
from home_application.utils.tools import check_user_is_admin, get_paginator

# 开发框架中通过中间件默认是需要登录态的，如有不需要登录的，可添加装饰器login_exempt
# 装饰器引入 from blueapps.account.decorators import login_exempt


@require_http_methods(["POST"])
@is_group_member(admin_needed=["POST"])
def add_user(request, group_id):
    """添加用户信息"""
    req = json.loads(request.body)
    new_user_ids = set(req.get("new_user_ids"))
    # 获取日报数据库中没有的用户，将其信息从蓝鲸平台拉取过来
    sign_in_user_ids = set(User.objects.filter(id__in=new_user_ids).values_list("id", flat=True))
    user_not_in_platform = new_user_ids - sign_in_user_ids
    # ↓↓↓当有不在本系统中的用户时去主平台拉取------------
    if len(user_not_in_platform):
        client = get_client_by_request(request=request)
        response = client.usermanage.list_users(
            lookup_field="id",
            exact_lookups=",".join(map(str, user_not_in_platform)),  # 将set中的整数拼接成","连接的字符串，用做从蓝鲸平台精准获取用户信息
            fields="id,username,display_name,email,telephone",
            page=1,
            pageSize=len(user_not_in_platform),
        )
        if not response.get("result"):
            return JsonResponse({"result": False, "code": 1, "message": "从蓝鲸主平台拉取用户时出现错误"})
        # 从蓝鲸主平台拿到的新用户
        user_infos = response.get("data").get("results")
        # 将新用户添加到数据库
        new_users = []
        for u_info in user_infos:
            new_users.append(
                User(
                    id=u_info["id"],
                    username=u_info["username"],
                    name=u_info["display_name"],
                    email=u_info["email"],
                    phone=u_info["telephone"],
                )
            )
        User.objects.bulk_create(new_users)
    # ↑↑↑拉取成功-----------------------------------

    # 添加组-用户表
    new_group_user = []
    for user_id in new_user_ids:
        new_group_user.append(GroupUser(user_id=user_id, group_id=group_id))
    GroupUser.objects.bulk_create(new_group_user)
    return JsonResponse({"result": True, "code": 0, "message": "添加用户成功", "data": []})


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


@require_GET
@is_group_member()
def report_filter(request, group_id):
    # 根据成员id分页获取他最近的日报-----------------------------------------------------------------------------
    member_id = request.GET.get("member_id")
    page = request.GET.get("page")
    # 每一页显示日报数量
    page_size = request.GET.get("size", 8)
    if member_id:
        # 根据member_id参数判断是根据成员id还是日期获取日报，
        try:
            # 安全校验，查看目标对象是否为同组成员
            GroupUser.objects.get(group_id=group_id, user_id=member_id)
            member_name = User.objects.get(id=member_id).username
        except GroupUser.DoesNotExist:
            return JsonResponse({"result": False, "code": -1, "message": "与目标用户非同组成员，查询被拒绝", "data": []})
        except User.DoesNotExist:
            return JsonResponse({"result": False, "code": -1, "message": "目标用户不存在", "data": []})
        except ValueError:
            return JsonResponse({"result": False, "code": -1, "message": "日报数量无效", "data": []})

        # 查询当前成员的日报，按照日期降序
        member_report = Daily.objects.filter(create_by=member_name).order_by("-date")
        total_report_num = member_report.count()

        # 分页
        member_report = get_paginator(member_report, page, page_size)
        if member_report is None:
            return JsonResponse({"result": False, "code": 404, "message": "分页参数异常", "data": []})
        # 查询完毕返回数据
        res_data = {"total_report_num": total_report_num, "reports": content_format_as_json(member_report)}
        return JsonResponse({"result": True, "code": 0, "message": "查询日报成功", "data": res_data})

    # 根据日期获取组内所有成员的日报------------------------------------------------------------------------------
    report_date = request.GET.get("date")
    try:
        report_date = datetime.strptime(report_date, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({"result": False, "code": -1, "message": "日期格式错误", "data": []})
    # 查询组内所有人
    # 首选获取组内成员的id，然后再去查询成员对应的username
    member_in_group = GroupUser.objects.filter(group_id=group_id).values_list("user_id", flat=True)
    member_in_group = User.objects.filter(id__in=member_in_group).values_list("username", flat=True)
    # 查询所有人的日报
    member_report = Daily.objects.filter(date=report_date, create_by__in=member_in_group).order_by("-date")
    total_report_num = member_report.count()
    # 查找自己的日报
    get_my_report = True
    if not CalendarHandler(report_date).is_holiday:
        try:
            Daily.objects.get(date=report_date, create_by=request.user.username)
        except Daily.DoesNotExist:
            get_my_report = False
    if check_user_is_admin(request, 0):
        get_my_report = True
    # 分页
    member_report = get_paginator(member_report, page, page_size)
    if member_report is None:
        return JsonResponse({"result": False, "code": 404, "message": "分页参数异常", "data": []})
    # 查询完毕返回数据
    res_data = {
        "total_report_num": total_report_num,
        "reports": content_format_as_json(member_report),
        "my_today_report": get_my_report,
    }
    return JsonResponse({"result": True, "code": 0, "message": "获取日报成功", "data": res_data})


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
