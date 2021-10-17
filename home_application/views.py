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
import time

from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render

# 开发框架中通过中间件默认是需要登录态的，如有不需要登录的，可添加装饰器login_exempt
# 装饰器引入 from blueapps.account.decorators import login_exempt
from django.utils.datetime_safe import datetime
from django.views.decorators.http import require_http_methods

from blueking.component.shortcuts import get_client_by_request
from home_application.models import DailyReportTemplate, Group
from home_application.utils.check_param import check_param
from home_application.utils.decorator import is_group_member


def home(request):
    """
    首页
    """
    return render(request, "index.html")


def dev_guide(request):
    """
    开发指引
    """
    return render(request, "home_application/dev_guide.html")


def contact(request):
    """
    联系页
    """
    return render(request, "home_application/contact.html")


def send_get_or_post_test(request):
    """
    测试前端发送的get请求和post请求是否正常
    """
    if request.method == "GET":
        return JsonResponse({"data": [], "message": f"Get请求发送成功{time.time()}"})
    if request.method == "POST":
        return JsonResponse({"data": [], "message": f"Post请求发送成功{time.time()}"})


@require_http_methods(["GET", "POST", "PATCH", "DELETE"])
@is_group_member(admin_needed=["POST", "PATCH", "DELETE"])
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
    if request.method == "PATCH":
        template_name = req.get("name")
        template_content = req.get("content")
        template_id = req.get("template_id")
        # 模板名字不可为空，但是模板内容支持为空
        if not template_name:
            return JsonResponse({"result": False, "code": -1, "message": "模板名不可为空", "data": []})

        # 构造更新数据
        template_update_data = {}
        if template_content is not None:
            template_update_data["content"] = template_content
        if template_name:
            template_update_data["name"] = template_name
        # 验证模板是否存在
        try:
            DailyReportTemplate.objects.filter(id=template_id, group_id=group_id).update(**template_update_data)
            return JsonResponse({"result": True, "code": 0, "message": "更新模板成功", "data": []})
        except DailyReportTemplate.DoesNotExist:
            return JsonResponse({"result": False, "code": -1, "message": "对应组不存在相关模板", "data": []})

    # 删除模板
    if request.method == "DELETE":
        template_id = req.get("template_id")
        # 尝试删除模板，找不到则返回异常
        try:
            DailyReportTemplate.objects.get(id=template_id, group_id=group_id).delete()
            return JsonResponse({"result": True, "code": 0, "message": "模板删除成功", "data": []})
        except DailyReportTemplate.DoesNotExist:
            return JsonResponse({"result": False, "code": -1, "message": "对应组不存在相关模板", "data": []})


def add_group(request):
    """添加组"""
    req = json.loads(request.body)
    params = {"name": "组名", "admin": "管理员"}
    check_result, message = check_param(params, req)
    if not check_result:
        return JsonResponse({"result": False, "code": 1, "message": message})
    name = req.get("name")
    admin = req.get("admin")
    try:
        Group.objects.create(name=name, admin=admin, create_by=request.user.username)
    except IntegrityError:
        return JsonResponse({"result": False, "code": 1, "message": "添加失败，组名重复"})
    else:
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
    admin = req.get("admin")
    try:
        Group.objects.filter(id=id).update(name=name, admin=admin, update_time=datetime.now())
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
