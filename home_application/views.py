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
import math
from datetime import timedelta

from django.db import IntegrityError
from django.http import JsonResponse

# 开发框架中通过中间件默认是需要登录态的，如有不需要登录的，可添加装饰器login_exempt
# 装饰器引入 from blueapps.account.decorators import login_exempt
from django.shortcuts import render
from django.utils.datetime_safe import datetime
from django.views.decorators.http import require_GET, require_http_methods

from blueking.component.shortcuts import get_client_by_request
from home_application.celery_task import (
    send_apply_for_group_result,
    send_apply_for_group_to_manager,
)
from home_application.models import (
    ApplyForGroup,
    Daily,
    DailyReportTemplate,
    FreeTime,
    Group,
    GroupUser,
    User,
)
from home_application.utils.calendar_util import CalendarHandler
from home_application.utils.decorator import is_group_member
from home_application.utils.report_operation import content_format_as_json
from home_application.utils.tools import (
    apply_info_to_json,
    apply_is_available_to_json,
    check_param,
    check_user_is_admin,
    get_paginator,
)


def home(request):
    """
    首页
    """
    from django.db import connection

    sql = (
        "UPDATE `home_application_group` g "
        "SET g.admin=REPLACE(REPLACE(REPLACE(g.admin, '\\'', ''), '[', ''), ']', '') "
        "WHERE INSTR(g.admin, '[') = 1 "
        "AND INSTR(g.admin, ']') = LENGTH(g.admin);"
    )
    with connection.cursor() as cursor:
        cursor.execute(sql)
    return render(request, "index.html")


def get_all_report_template(request):
    """
    获取用户所在组的所有的日报模板
    """
    # 默认的日报模板
    templates = [
        {"id": 0, "name": "日报", "content": "今日总结;明日计划;感想", "create_by": "系统默认", "create_name": "系统默认", "group_id": 0}
    ]

    user_id = request.user.id
    groups_id = GroupUser.objects.filter(user_id=user_id).values_list("group_id", flat=True)
    groups = Group.objects.filter(id__in=groups_id)
    group_id_name_map = {}
    for g in groups:
        group_id_name_map[g.id] = g.name
    group_templates = list(DailyReportTemplate.objects.filter(group_id__in=groups_id).values())
    for t in group_templates:
        t["name"] += "(%s)" % (group_id_name_map[t["group_id"]])
    templates.extend(group_templates)
    return JsonResponse({"result": True, "code": 0, "message": "", "data": templates})


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

    # 删除模板
    if request.method == "DELETE":
        template_id = request.GET.get("template_id")
        # 尝试删除模板，找不到则返回异常
        try:
            DailyReportTemplate.objects.get(id=template_id, group_id=group_id).delete()
            return JsonResponse({"result": True, "code": 0, "message": "模板删除成功", "data": []})
        except DailyReportTemplate.DoesNotExist:
            return JsonResponse({"result": False, "code": -1, "message": "对应组不存在相关模板", "data": []})

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
        try:
            create_name = User.objects.get(username=request.user.username).name
        except User.DoesNotExist:
            return JsonResponse({"result": False, "code": -1, "message": "当前用户不存在", "data": []})
        DailyReportTemplate.objects.create(
            name=template_name,
            content=template_content,
            create_by=request.user.username,
            create_name=create_name,
            group_id=group_id,
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


@is_group_member()
def get_group_info(request, group_id):
    group = Group.objects.get(id=group_id)
    admin_usernames = group.admin_list
    admin_list = User.objects.filter(username__in=admin_usernames).values("id", "username", "name")
    data = {
        "id": group.id,
        "name": group.name,
        "admin": group.admin,
        "admin_list": list(admin_list),
        "create_by": group.create_by,
        "create_name": group.create_name,
        "create_time": group.create_time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    return JsonResponse({"result": True, "code": 0, "message": "获取组信息成功", "data": data})


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
    has_create_user = False
    for admin in admins:
        admin_names.append(admin.get("username"))
        if admin.get("username") == request.user.username:
            has_create_user = True
            create_name = admin.get("display_name")
    if has_create_user is False:
        return JsonResponse({"result": False, "code": 1, "message": "创建人未在管理员中"})
    try:
        group = Group.objects.create(
            name=name, admin=",".join(admin_names), create_by=request.user.username, create_name=create_name
        )
    except IntegrityError:
        return JsonResponse({"result": False, "code": 1, "message": "添加失败，组名重复"})
    else:
        # 添加未注册的用户信息
        auto_sign_users(admin_names, admins)
        # 添加组-用户信息
        group_user_list = []
        for admin in admins:
            group_user_list.append(GroupUser(group_id=group.id, user_id=admin.get("id")))
        GroupUser.objects.bulk_create(group_user_list)
        return JsonResponse({"result": True, "code": 0, "message": "添加成功", "data": {"group_id": group.id}})


@is_group_member(admin_needed=["POST"])
def delete_group(request, group_id):
    try:
        DailyReportTemplate.objects.filter(group_id=group_id).delete()
        GroupUser.objects.filter(group_id=group_id).delete()
        Group.objects.get(id=group_id).delete()
        return JsonResponse({"result": True, "code": 0, "message": "删除组成功", "data": []})
    except Group.DoesNotExist:
        return JsonResponse({"result": True, "code": 0, "message": "组不存在", "data": []})


@is_group_member(admin_needed=["POST", "PUT", "DELETE"])
def update_group(request, group_id):
    """编辑组信息"""
    req = json.loads(request.body)
    params = {"name": "组名", "admin": "管理员"}
    check_result, message = check_param(params, req)
    if not check_result:
        return JsonResponse({"result": False, "code": 1, "message": message})
    name = req.get("name")
    admins = req.get("admin")
    admin_names = []
    admin_ids = []
    for admin in admins:
        admin_ids.append(admin.get("id"))
        admin_names.append(admin.get("username"))
    # 添加未注册的用户信息
    auto_sign_users(admin_names, admins)
    # 批量添加用户-组信息
    exist_user_ids = GroupUser.objects.filter(group_id=group_id, user_id__in=admin_ids).values("user_id")
    group_user_list = []
    for admin_id in admin_ids:
        if not {"user_id": admin_id} in exist_user_ids:
            group_user_list.append(GroupUser(group_id=group_id, user_id=admin_id))
    GroupUser.objects.bulk_create(group_user_list)
    try:
        Group.objects.filter(id=group_id).update(name=name, admin=",".join(admin_names), update_time=datetime.now())
    except IntegrityError:
        return JsonResponse({"result": False, "code": 1, "message": "更新失败，组名重复"})
    else:
        return JsonResponse({"result": True, "code": 0, "message": "更新成功", "data": []})


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


def get_available_apply_groups(request):
    """获取所有(未在、未申请)组信息"""
    # 获取用户已经在的组
    sql_str = (
        "select g.id, g.name, if (gu.id is null, if(apply.id is null, true, false), false) is_available "
        "from home_application_group g "
        "left join home_application_groupuser gu "
        "on g.id = gu.group_id and gu.user_id = %s "
        "left join home_application_applyforgroup apply "
        "on g.id = apply.group_id and apply.user_id = %s and apply.status = 0"
    )
    group_infos = Group.objects.raw(sql_str, [request.user.id, request.user.id])
    group_list = [apply_is_available_to_json(group) for group in group_infos]
    return JsonResponse({"result": True, "code": 0, "message": "获取成功", "data": group_list})


def apply_for_group(request):
    """用户申请入组"""
    req = json.loads(request.body)
    params = {"group_id": "组id"}
    check_result, message = check_param(params, req)
    if not check_result:
        return JsonResponse({"result": False, "code": 1, "message": message})
    group_id = req.get("group_id")
    user_id = request.user.id
    # 获取组信息
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return JsonResponse({"result": False, "code": 0, "message": "组不存在", "data": []})
    # 检查是否已在组中
    try:
        GroupUser.objects.get(group_id=group_id, user_id=user_id)
        # 用户已在组中
        return JsonResponse({"result": False, "code": 0, "message": u"用户已在组-{}中".format(group.name), "data": []})
    except GroupUser.DoesNotExist:
        # 用户不在组中
        try:
            ApplyForGroup.objects.get(group_id=group_id, user_id=user_id, status=0)
            # 用户已申请过入组
            return JsonResponse({"result": False, "code": 0, "message": u"已申请过入组-{}".format(group.name), "data": []})
        except ApplyForGroup.DoesNotExist:
            # 用户未申请入组
            ApplyForGroup.objects.create(group_id=group_id, user_id=user_id, status=0)
            # 给管理员发送邮件
            # 获取用户信息
            user = User.objects.get(id=user_id)
            send_apply_for_group_to_manager.apply_async(
                kwargs={
                    "group_name": group.name,
                    "group_admins": group.admin,
                    "user_name": "{}({})".format(user.username, user.name),
                    "group_id": group_id,
                }
            )
            return JsonResponse({"result": True, "code": 0, "message": u"申请入组-{}成功".format(group.name), "data": []})


@is_group_member(admin_needed=["GET"])
def get_apply_for_group_users(request, group_id):
    """ "获取申请入组列表"""
    # 获取所有申请人id和申请时间
    sql_str = (
        "select user.id, user.username, user.name,apply.update_time "
        "from home_application_applyforgroup apply, home_application_user user "
        "where apply.user_id = user.id and apply.status = 0 and apply.group_id = %s"
    )
    apply_infos = ApplyForGroup.objects.raw(sql_str, [group_id])
    apply_info_list = [apply_info_to_json(info) for info in apply_infos]
    return JsonResponse({"result": True, "code": 0, "message": "获取申请人列表成功", "data": apply_info_list})


@is_group_member(admin_needed=["POST"])
def deal_join_group(request, group_id):
    """管理员同意用户入组"""
    # 校验参数
    req = json.loads(request.body)
    params = {"user_id": "用户id", "status": "处理操作"}
    check_result, message = check_param(params, req)
    if not check_result:
        return JsonResponse({"result": False, "code": 1, "message": message})
    user_id = req.get("user_id")
    # 操作 status = 1(同意), status = 2(拒绝)
    status = req.get("status")
    if status == 1:
        status_message = "同意"
    elif status == 2:
        status_message = "拒绝"
    else:
        return JsonResponse({"result": False, "code": 0, "message": "参数status传值不合法", "data": []})
    try:
        # 获取用户信息
        user = User.objects.get(id=user_id)
        # 前端显示用户信息username(name)
        user_name = u"{}({})".format(user.username, user.name)
        # 前端显示组名
        group_name = Group.objects.get(id=group_id).name
        # 如果允许入组，添加组-用户信息（入组）
        if status == 1:
            GroupUser.objects.create(group_id=group_id, user_id=user_id)
        # 更改申请入组状态
        ApplyForGroup.objects.filter(group_id=group_id, user_id=user_id).update(
            status=status, operator=request.user.id, update_time=datetime.now()
        )
        # 发送申请结果给用户
        send_apply_for_group_result.apply_async(
            kwargs={"username": user.username, "group_name": group_name, "status": status}
        )
    except User.DoesNotExist:
        return JsonResponse({"result": False, "code": 0, "message": u"用户(id={})不存在".format(user_id), "data": []})
    except Group.DoesNotExist:
        return JsonResponse({"result": False, "code": 0, "message": u"组（id={}）不存在".format(group_id), "data": []})
    except IntegrityError:
        return JsonResponse({"result": False, "code": 0, "message": u"用户已在组-{}中".format(group_name), "data": []})
    return JsonResponse(
        {
            "result": True,
            "code": 0,
            "message": u"{}{}入组({})成功".format(status_message, user_name, group_name),
            "data": [],
        }
    )


def get_user_groups(request):
    """查询用户组列表"""
    user_id = request.user.id
    group_ids = GroupUser.objects.filter(user_id=user_id).values_list("group_id", flat=True)
    groups = Group.objects.in_bulk(list(group_ids))
    group_list = []
    for group in groups.values():
        admin = group.admin_list
        group_list.append(
            {
                "id": group.id,
                "name": group.name,
                "admin": admin,
                "create_by": group.create_by,
                "create_name": group.create_name,
                "create_time": group.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
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


def exit_group(request, group_id):
    """组内移除用户（可能不是当前用户），用户退出组"""
    req = json.loads(request.body)
    params = {"user_id": "用户id"}
    check_result, message = check_param(params, req)
    if not check_result:
        return JsonResponse({"result": False, "code": 1, "message": message})
    user_id = req.get("user_id")
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
        # 获取日期
        date = request.GET.get("date")
        if date:
            try:
                date = datetime.strptime(date, "%Y-%m-%d").date()
                today_report = Daily.objects.get(create_by=request.user.username, date=date)
                return JsonResponse({"result": True, "code": 0, "message": "获取今天日报成功", "data": today_report.to_json()})
            except ValueError:
                return JsonResponse({"result": False, "code": -1, "message": "日期格式错误", "data": []})
            except Daily.DoesNotExist:
                return JsonResponse({"result": True, "code": 0, "message": "今天还没有写日报", "data": {}})

    # 参数校验-----------------------------------------------------------------------------------------
    req = json.loads(request.body)
    report_content = req.get("content")
    report_date_str = req.get("date")
    template_id = req.get("template_id")
    try:
        template_id = int(template_id)
        report_date = datetime.strptime(report_date_str, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({"result": False, "code": -1, "message": "日期或模板id数据格式错误", "data": []})
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
            target_report.template_id = template_id
            target_report.save()
            message = "修改日报成功"
        except Daily.DoesNotExist:
            # 抛出异常表示找不到，说明还没有写日报，可以添加新的日报
            create_name = User.objects.get(username=request.user.username).name

            # 如果是补签之前的日报直接修改发送状态为'已发送'，但是在当天10点之前补签昨天的日报仍为'未发送'
            datetime_now = datetime.now()
            if datetime_now.hour < 10:
                # 填写日期在10点前，日报日期在昨天(今天-1天)之前就是补签
                send_status = report_date < (datetime_now - timedelta(days=1)).date()
            else:
                # 填写日期在10点后，日报日期小于当天就是补签
                send_status = report_date < datetime_now.date()

            Daily.objects.create(
                content=report_content,
                create_by=request.user.username,
                create_name=create_name,
                date=report_date,
                template_id=template_id,
                send_status=send_status,
                is_normal=not send_status,
            )
            if send_status:
                message = "补写日报成功"
            else:
                message = "保存日报成功"
        return JsonResponse({"result": True, "code": 0, "message": message, "data": []})


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


@require_GET
def get_reports_dates(request):
    """获取用户已提交的所有日报日期"""
    member_dates = Daily.objects.filter(create_by=request.user.username, send_status=True).values_list(
        "date", flat=True
    )
    return JsonResponse({"result": True, "code": 0, "message": "获取日报成功", "data": list(member_dates)})


@require_GET
def check_yesterday_daily(request):
    """检查工作日日报是否已填写"""
    yesterday = datetime.now() - timedelta(days=1)
    if check_user_is_admin(request, 0):
        return JsonResponse({"result": True, "code": 0, "message": "管理员不需写日报", "data": True})
    if CalendarHandler(yesterday).is_holiday:
        return JsonResponse({"result": True, "code": 0, "message": "昨天非工作日", "data": []})
    try:
        Daily.objects.get(create_by=request.user.username, date=yesterday)
    except Daily.DoesNotExist:
        return JsonResponse({"result": False, "code": 0, "message": "昨天没有写日报", "data": []})
    return JsonResponse({"result": True, "code": 0, "message": "昨天已写日报", "data": []})


@is_group_member(admin_needed=["PATCH"])
def update_daily_perfect_status(request, group_id, daily_id):
    """修改日报的优秀状态"""
    try:
        daily = Daily.objects.get(id=daily_id)
        Daily.objects.filter(id=daily_id).update(is_perfect=not daily.is_perfect)
    except Daily.DoesNotExist:
        return JsonResponse({"result": False, "code": 1, "message": "日报不存在", "data": []})
    return JsonResponse({"result": True, "code": 0, "message": "修改日报是否优秀状态成功", "data": []})


@require_GET
@is_group_member()
def get_prefect_dailys(request, group_id):
    """获取组内优秀日报"""
    # 根据组查询组所有成员用户名
    member_ids = GroupUser.objects.filter(group_id=group_id).values_list("user_id", flat=True)
    member_usernames = User.objects.filter(id__in=member_ids).values_list("username", flat=True)
    select_type = request.GET.get("select_type")
    # 查询所有优秀日报
    daily_list = Daily.objects.filter(create_by__in=member_usernames, is_perfect=True).order_by("-date")
    if select_type == "month":
        # 查询某月优秀日报
        year = request.GET.get("year")
        month = request.GET.get("month")
        daily_list = daily_list.filter(date__year=year, date__month=month)
    # 日报数量
    total_num = daily_list.count()
    # 分页
    page = request.GET.get("page")
    size = request.GET.get("size")
    daily_list = get_paginator(daily_list, page=page, size=size)
    if daily_list is None:
        return JsonResponse({"result": False, "code": 404, "message": "分页参数异常", "data": []})
    # 返回日报数据
    res_data = {
        "total_num": total_num,
        "daily_list": content_format_as_json(daily_list),
    }
    return JsonResponse({"result": True, "code": 0, "message": "获取优秀日报成功", "data": res_data})


@require_http_methods(["GET", "POST"])
def free_time_get_post(request):
    """空闲时间的增删改查"""
    # 查
    if request.method == "GET":
        # 要查询空闲时间的起止日期
        start_date = request.GET.get("start_date", "")
        end_date = request.GET.get("end_date", "")
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
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
                f_time["start_time"] = datetime.strptime(f_time["start_time"], "%Y-%m-%d %H:%M")
                f_time["end_time"] = datetime.strptime(f_time["end_time"], "%Y-%m-%d %H:%M")

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
            free_time_obj.start_time = datetime.strptime(new_start_time, "%Y-%m-%d %H:%M")
            free_time_obj.end_time = datetime.strptime(new_end_time, "%Y-%m-%d %H:%M")
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
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        if start_date > end_date:
            return JsonResponse({"result": False, "code": 1, "message": "结束日期不得早于起始日期", "data": []})
    except ValueError:
        return JsonResponse({"result": False, "code": 1, "message": "日期格式错误", "data": []})

    user_ids = GroupUser.objects.filter(group_id=group_id).values_list("user_id", flat=True)
    usernames = User.objects.filter(id__in=user_ids).values_list("username", flat=True)
    free_times = FreeTime.objects.get_free_time(usernames, start_date, end_date)
    return JsonResponse({"result": True, "code": 0, "message": "", "data": free_times})


@is_group_member(admin_needed=["POST"])
def check_user_in_group(request, group_id):
    # 查询成员是否已加入指定小组，返回未加入小组的成员姓名
    user_name = json.loads(request.body).get("UserName")
    # 待查询姓名列表
    user_name_list = str(user_name).split(" ")
    id_list = GroupUser.objects.filter(group_id=group_id).values_list("user_id", flat=True)
    joined_user_name_list = User.objects.filter(id__in=id_list).values_list("name", flat=True)
    unjoined_users = []
    for u in user_name_list:
        if u not in joined_user_name_list:
            unjoined_users.append(u)
    if len(unjoined_users) > 0:
        return JsonResponse({"result": True, "code": 0, "message": "", "data": ",".join(unjoined_users) + "未加入当前小组"})
    return JsonResponse({"result": True, "code": 0, "message": "", "data": "查询的用户已加入当前小组中"})


@require_http_methods(["GET"])
def check_user_admin(request):
    user_is_admin = check_user_is_admin(request, 1)
    return JsonResponse({"result": user_is_admin, "code": 200, "message": "", "data": []})
