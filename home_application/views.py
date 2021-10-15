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

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from home_application.models import DailyReportTemplate, TemplateGroup
from home_application.utils.decorator import is_group_admin


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


@require_http_methods(["POST", "PATCH"])
@is_group_admin
def report_template(request, group_id):
    """
    创建或者更新日报模板
    """
    username = request.user.username

    req = json.loads(request.body.decode())
    template_name = req.get("name")
    template_content = req.get("content")

    # 模板名字不可为空，但是模板内容支持为空
    if not template_name:
        return JsonResponse({"result": False, "code": -1, "message": "模板名不可为空", "data": []})

    if request.method == "POST":
        # 数据合法，创建新的日报模板
        if template_content is None:
            template_content = ""
        new_template = DailyReportTemplate.objects.create(
            name=template_name, content=template_content, create_by=username
        )  # noqa
        TemplateGroup.objects.create(group_id=group_id, template_id=new_template.id)
        return JsonResponse({"result": True, "code": 0, "message": "创建日报模板成功", "data": []})
    elif request.method == "PATCH":
        template_id = req.get("template_id")

        # 构造更新数据
        template_update_date = {}
        if template_content is not None:
            template_update_date["content"] = template_content
        if template_name:
            template_update_date["name"] = template_name
        # 验证模板是否存在
        try:
            TemplateGroup.objects.get(group_id=group_id, template_id=template_id)
            DailyReportTemplate.objects.filter(id=template_id).update(**template_update_date)
            return JsonResponse({"result": True, "code": 0, "message": "更新模板成功", "data": []})
        except (DailyReportTemplate.DoesNotExist, TemplateGroup.DoesNotExist):
            return JsonResponse({"result": False, "code": -1, "message": "对应组不存在相关模板", "data": []})
