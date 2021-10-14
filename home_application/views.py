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

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import render

from home_application.models import DailyReportTemplate, Group, TemplateGroup


# 开发框架中通过中间件默认是需要登录态的，如有不需要登录的，可添加装饰器login_exempt
# 装饰器引入 from blueapps.account.decorators import login_exempt
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


def create_report_template(request):
    """
    创建日报模板
    """
    # 存储返回结果
    result = {"result": False, "code": 400, "message": "", "data": []}

    if request.method != "POST":
        result["message"] = "请使用POST方法请求"
        return JsonResponse(status=result["code"], data=result)

    username = request.user.username
    template_name = request.POST.get("name", None)
    template_content = request.POST.get("content", "")
    group_id = request.POST.get("group_id", None)

    # 模板名字不可为空，但是模板内容支持为空
    if not (template_name and group_id):
        result["message"] = "缺少请求参数"
        return JsonResponse(status=result["code"], data=result)

    # 验证组是否存在以及是否拥有管理员权限
    try:
        temp_group = Group.objects.get(id=group_id)
    except ObjectDoesNotExist:
        result["message"] = "未找到对应的组"
        return JsonResponse(status=result["code"], data=result)
    if not temp_group.admin_include(username=username):
        result["code"] = 403
        result["message"] = "没有对应组的管理权限"
        return JsonResponse(status=result["code"], data=result)

    # 数据合法，创建新的日报模板
    new_template = DailyReportTemplate.objects.create(name=template_name, content=template_content, create_by=username)
    TemplateGroup.objects.create(group_id=group_id, template_id=new_template.id)

    result["result"] = True
    result["code"] = 200
    result["message"] = "创建日报模板成功"
    return JsonResponse(result)


def update_report_template(request):
    """
    更新日报模板
    """
    # 存储返回结果
    result = {"result": False, "code": 400, "message": "", "data": []}

    if request.method != "PUT":
        result["message"] = "请使用PUT方法请求"
        return JsonResponse(status=result["code"], data=result)

    req = json.loads(request.body.decode())
    username = request.user.username
    group_id = req.get("group_id", None)
    template_id = req.get("template_id", None)
    new_name = req.get("name", None)
    new_content = req.get("content", None)

    # 若模板名字非空则创建，允许模板内容为空
    if not (group_id and template_id):
        result["message"] = "缺少请求参数"
        return JsonResponse(status=result["code"], data=result)

    # 验证组和模板是否存在以及是否拥有管理员权限
    try:
        temp_group = Group.objects.get(id=group_id)
        temp_template = DailyReportTemplate.objects.get(id=template_id)
    except ObjectDoesNotExist:
        result["message"] = "未找到对应的组或者日报模板"
        return JsonResponse(status=result["code"], data=result)
    if not temp_group.admin_include(username=username):
        result["code"] = 403
        result["message"] = "没有对应组的管理权限"
        return JsonResponse(status=result["code"], data=result)

    # 修改模板内容
    if new_content is not None:
        temp_template.content = new_content
    if new_name:
        temp_template.name = new_name
    temp_template.save()
    result["result"] = True
    result["code"] = 200
    result["message"] = "修改日报模板成功"
    return JsonResponse(result)
