# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import json

from django.db import IntegrityError
from django.http import JsonResponse

# 开发框架中通过中间件默认是需要登录态的，如有不需要登录的，可添加装饰器login_exempt
# 装饰器引入 from blueapps.account.decorators import login_exempt
from django.shortcuts import render
from django.utils.datetime_safe import datetime
from django.views.decorators.http import require_GET, require_http_methods

from blueking.component.shortcuts import get_client_by_request
from home_application.models import Daily, DailyReportTemplate, Group, GroupUser, User
from home_application.utils.decorator import is_group_member
from home_application.utils.tools import check_param


def home(request):
    """
    首页
    """
    return render(request, "index.html")


@require_http_methods(["GET", "POST", "PUT", "DELETE"])
@is_group_member(admin_needed=["POST", "PUT", "DELETE"])
def report_template(request, group_id):
    """
    日报模板的增删改查功能
    """
    # 获取模板
    if request.method == "GET":
        templates = list(DailyReportTemplate.objects.filter(group_id=group_id).values())
        return JsonResponse({"result": True, "code": 0, "message": "", "data": templates})

    req = json.loads(request.body)

    # 创建模板
    if request.method == "POST":
        template_name = req.get("name")
        template_content = req.get("content")
        # 模板名字不可为空，但是模板内容支持为空
        if not template_name:
            return JsonResponse({"result": False, "code": -1, "message": "模板名不可为空", "data": []})

        # 数据合法，创建新的日报模板
        if template_content is None:
            template_content = ""
        DailyReportTemplate.objects.create(
            name=template_name, content=template_content, create_by=request.user.username, group_id=group_id
        )
        return JsonResponse({"result": True, "code": 0, "message": "创建日报模板成功", "data": []})

    # 修改模板
    if request.method == "PUT":
        template_name = req.get("name")
        template_content = req.get("content")
        template_id = req.get("template_id")
        # 模板名字不可为空，但是模板内容支持为空
        if not template_name:
            return JsonResponse({"result": False, "code": -1, "message": "模板名不可为空", "data": []})

        # 验证模板是否存在，存在则更新模板
        try:
            target_template = DailyReportTemplate.objects.get(id=template_id, group_id=group_id)
        except DailyReportTemplate.DoesNotExist:
            return JsonResponse({"result": False, "code": -1, "message": "对应组不存在相关模板", "data": []})
        target_template.content = template_content
        target_template.name = template_name
        target_template.save()
        return JsonResponse({"result": True, "code": 0, "message": "更新模板成功", "data": []})

    # 删除模板
    if request.method == "DELETE":
        template_id = req.get("template_id")
        # 尝试删除模板，找不到则返回异常
        try:
            DailyReportTemplate.objects.get(id=template_id, group_id=group_id).delete()
            return JsonResponse({"result": True, "code": 0, "message": "模板删除成功", "data": []})
        except DailyReportTemplate.DoesNotExist:
            return JsonResponse({"result": False, "code": -1, "message": "对应组不存在相关模板", "data": []})


@is_group_member()
def get_group_info(request, group_id):
    return JsonResponse(
        {"result": True, "code": 0, "message": "获取组信息成功", "data": Group.objects.get(id=group_id).to_json()}
    )


def add_group(request):
    """添加组"""
    req = json.loads(request.body)
    params = {"name": "组名", "admin": "管理员"}
    check_result, message = check_param(params, req)
    if not check_result:
        return JsonResponse({"result": False, "code": 1, "message": message})
    name = req.get("name")
    admins = req.get("admin")
    admin_names = []  # 管理员username连接字符串
    for admin in admins:
        admin_names.append(admin.get("username"))
    try:
        group = Group.objects.create(name=name, admin=admin_names, create_by=request.user.username)
    except IntegrityError:
        return JsonResponse({"result": False, "code": 1, "message": "添加失败，组名重复"})
    else:
        # 批量新传来的用户信息
        # 查询已经存在的用户信息
        exist_users = User.objects.filter(username__in=admin_names).values("username")
        admin_list = []
        for admin in admins:
            if not {"username": admin.get("username")} in exist_users:
                # 除去已经存在的用户，添加新用户
                admin_list.append(
                    User(
                        id=admin.get("id"),
                        username=admin.get("username"),
                        name=admin.get("name"),
                        phone=admin.get("phone"),
                        email=admin.get("email"),
                    )
                )
        User.objects.bulk_create(admin_list)  # 注册未曾注册的管理员用户
        # 添加组-用户信息
        group_user_list = []
        for admin in admins:
            group_user_list.append(GroupUser(group_id=group.id, user_id=admin.get("id")))
        GroupUser.objects.bulk_create(group_user_list)
        return JsonResponse({"result": True, "code": 0, "message": "添加成功", "data": []})


def update_group(request):
    """编辑组信息"""
    req = json.loads(request.body)
    params = {"id": "组id", "name": "组名", "admin": "管理员"}
    check_result, message = check_param(params, req)
    if not check_result:
        return JsonResponse({"result": False, "code": 1, "message": message})
    id = req.get("id")
    name = req.get("name")
    admins = req.get("admin")
    admin_names = []
    admin_ids = []
    for admin in admins:
        admin_ids.append(admin.get("id"))
        admin_names.append(admin.get("username"))
    # 添加未注册的用户信息
    exist_users = User.objects.filter(username__in=admin_names).values("username")
    admin_list = []
    for admin in admins:
        if not {"username": admin.get("username")} in exist_users:
            admin_list.append(
                User(
                    id=admin.get("id"),
                    username=admin.get("username"),
                    name=admin.get("name"),
                    phone=admin.get("phone"),
                    email=admin.get("email"),
                )
            )
    User.objects.bulk_create(admin_list)  # 注册未曾注册的管理员用户
    # 批量添加用户-组信息
    exist_user_ids = GroupUser.objects.filter(group_id=id, user_id__in=admin_ids).values("user_id")
    group_user_list = []
    for admin_id in admin_ids:
        if not {"user_id": admin_id} in exist_user_ids:
            group_user_list.append(GroupUser(group_id=id, user_id=admin_id))
    GroupUser.objects.bulk_create(group_user_list)
    try:
        Group.objects.filter(id=id).update(name=name, admin=admin_names, update_time=datetime.now())
    except IntegrityError:
        return JsonResponse({"result": False, "code": 1, "message": "更新失败，组名重复"})
    else:
        return JsonResponse({"result": True, "code": 0, "message": "更新成功", "data": []})


def get_all_bk_users(request):
    """从蓝鲸平台，拉取所有用户列表"""
    client = get_client_by_request(request=request)
    response = client.usermanage.list_users(fields="id,username,display_name,email,telephone")
    result = response.get("result")
    if result:
        return JsonResponse({"result": True, "code": 0, "data": response.get("data"), "message": "获取蓝鲸用户列表成功"})
    else:
        # 请求接口成功，但获取内容失败，返回错误信息
        return response


@require_http_methods(["POST"])
@is_group_member(admin_needed=["POST"])
def add_user(request, group_id):
    """添加用户信息"""
    req = json.loads(request.body)
    params = {"id": "用户id", "username": "用户名"}
    check_result, message = check_param(params, req)
    if not check_result:
        return JsonResponse({"result": False, "code": 1, "message": message})
    id = req.get("id")
    username = req.get("username")
    name = req.get("name")
    phone = req.get("phone")
    email = req.get("email")
    # 判断用户是否存在
    try:
        User.objects.get(id=id)  # 用户已存在
    except User.DoesNotExist:
        try:
            # 用户不存在，创建用户
            User.objects.create(id=id, username=username, name=name, phone=phone, email=email)
        except IntegrityError:
            return JsonResponse({"result": False, "code": 1, "message": "创建用户失败，用户名重复"})
    # 添加组-用户表
    try:
        GroupUser.objects.create(group_id=group_id, user_id=id)
    except IntegrityError:
        return JsonResponse({"result": True, "code": 0, "message": "用户已在组中", "data": []})
    return JsonResponse({"result": True, "code": 0, "message": "添加用户成功", "data": []})


def get_user(request):
    """获取当前用户信息"""
    user = (
        User.objects.filter(username=request.user.username).values("id", "username", "name", "phone", "email").first()
    )
    return JsonResponse({"result": True, "code": 0, "message": "查询成功", "data": user})


def update_user(request):
    """更改用户信息"""
    req = json.loads(request.body)
    name = req.get("name")
    phone = req.get("phone")
    email = req.get("email")
    try:
        User.objects.filter(id=request.user.id).update(name=name, phone=phone, email=email, update_time=datetime.now())
    except IntegrityError:
        return JsonResponse({"result": False, "code": 1, "message": "更新失败，用户名已存在"})
    else:
        return JsonResponse({"result": True, "code": 0, "message": "更新成功", "data": []})


def get_user_groups(request):
    """查询用户组列表"""
    user_id = request.user.id
    group_ids = GroupUser.objects.filter(user_id=user_id).values_list("group_id", flat=True)
    groups = Group.objects.in_bulk(list(group_ids))
    group_list = []
    for group in groups.values():
        group_list.append({"id": group.id, "name": group.name, "admin": group.admin})
    return JsonResponse({"result": True, "code": 0, "message": "查询成功", "data": group_list})


def get_group_users(request, group_id):
    """查询组的成员列表"""
    user_ids = GroupUser.objects.filter(group_id=group_id).values_list("user_id", flat=True)
    users = User.objects.in_bulk(list(user_ids))
    user_list = []
    for user in users.values():
        user_list.append(
            {"id": user.id, "username": user.username, "name": user.name, "phone": user.phone, "email": user.email}
        )
    return JsonResponse({"result": True, "code": 0, "message": "查询成功", "data": user_list})


def exit_group(request):
    """组内移除用户（可能不是当前用户），用户退出组"""
    req = json.loads(request.body)
    params = {"group_id": "组id", "username": "用户名"}
    check_result, message = check_param(params, req)
    if not check_result:
        return JsonResponse({"result": False, "code": 1, "message": message})
    group_id = req.get("group_id")
    user_id = User.objects.get(username=req.get("username")).id
    try:
        GroupUser.objects.get(group_id=group_id, user_id=user_id).delete()
    except GroupUser.DoesNotExist:
        return JsonResponse({"result": False, "code": 1, "message": "该用户不在组中"})
    return JsonResponse({"result": True, "code": 0, "message": "移除成功", "data": []})


@require_http_methods(["POST", "GET"])
def daily_report(request):
    """日报模块的增删改查"""
    # 获取今天的日报，没有就返回空-------------------------------------------------------------------------------
    if request.method == "GET":
        try:
            today_report = Daily.objects.get(create_by=request.user.username, date=datetime.today())
            return JsonResponse({"result": True, "code": 0, "message": "获取今天日报成功", "data": today_report.to_json()})
        except Daily.DoesNotExist:
            return JsonResponse({"result": True, "code": 0, "message": "今天还没有写日报", "data": {}})

    # 参数校验-----------------------------------------------------------------------------------------
    req = json.loads(request.body)
    report_content = req.get("content")
    report_date = req.get("date")
    if not isinstance(report_content, dict):
        return JsonResponse({"result": False, "code": -1, "message": "日报内容格式错误", "data": []})
    try:
        report_date = datetime.strptime(report_date, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({"result": False, "code": -1, "message": "日期格式错误", "data": []})
    if report_date > datetime.today():
        return JsonResponse({"result": False, "code": -1, "message": "日期不合法", "data": []})

    # 添加或修改日报--------------------------------------------------------------------------------------
    if request.method == "POST":
        try:
            # 修改日报
            target_report = Daily.objects.get(create_by=request.user.username, date=report_date)
            # 日报如果已经发送管理员审核的话就直接返回不可修改
            if target_report.send_status:
                return JsonResponse({"result": False, "code": -1, "message": "日报已经发送管理员查看，不可修改", "data": []})
            target_report.content = report_content
            target_report.save()
            return JsonResponse({"result": True, "code": 0, "message": "修改日报成功", "data": []})
        except Daily.DoesNotExist:
            # 抛出异常表示找不到，说明还没有写日报，可以添加新的日报
            Daily.objects.create(
                content=report_content, create_by=request.user.username, date=report_date, send_status=False
            )
            return JsonResponse({"result": True, "code": 0, "message": "添加日报成功", "data": []})


@require_GET
@is_group_member()
def report_filter(request, group_id):
    # 根据成员id分页获取他最近的日报-----------------------------------------------------------------------------
    member_id = request.GET.get("member_id")
    if member_id:
        # 如果有该参数则说明是根据成员id获取日报，
        # 没有则直接跳到下边根据组和日期获取所有成员对应日期的日报
        try:
            # 安全校验，查看目标对象是否为同组成员
            GroupUser.objects.get(group_id=group_id, user_id=member_id)
            member_name = User.objects.get(id=member_id).username
            # 参数校验
            report_num = int(request.GET.get("report_num", 5))
        except GroupUser.DoesNotExist:
            return JsonResponse({"result": False, "code": -1, "message": "与目标用户非同组成员，查询被拒绝", "data": []})
        except User.DoesNotExist:
            return JsonResponse({"result": False, "code": -1, "message": "目标用户不存在", "data": []})
        except ValueError:
            return JsonResponse({"result": False, "code": -1, "message": "日报数量无效", "data": []})

        # 查询当前成员的日报，按照日期降序
        member_report = Daily.objects.filter(create_by=member_name).order_by("-date")
        total_report_num = member_report.count()
        if report_num > 0:
            member_report = member_report[:report_num]
        # 查询完毕返回数据
        res_data = {"total_report_num": total_report_num, "reports": list(member_report.values())}
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
    member_report = list(Daily.objects.filter(date=report_date, create_by__in=member_in_group).values())
    return JsonResponse({"result": True, "code": 0, "message": "获取日报成功", "data": member_report})
