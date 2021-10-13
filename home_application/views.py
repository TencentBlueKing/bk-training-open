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
import time

from django.http import JsonResponse
from django.shortcuts import render

# 开发框架中通过中间件默认是需要登录态的，如有不需要登录的，可添加装饰器login_exempt
# 装饰器引入 from blueapps.account.decorators import login_exempt
from django.utils.datetime_safe import datetime
from kombu.utils import json

from blueking.component.shortcuts import get_client_by_request
from home_application.models import Group


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


def add_group(request):
    """添加组"""
    req = json.loads(request.body.decode("UTF-8"))
    try:
        name = req.get("name")
        admin = req.get("admin")
        Group.objects.create(name=name, admin=admin, create_by=request.user.username)
    except Exception as err:
        result = False
        message = str(err)
        return JsonResponse({"result": result, "code": 1, "message": message})
    else:
        result = True
        return JsonResponse({"result": result, "code": 0, "data": []})


def update_group(request):
    """编辑组信息"""
    req = json.loads(request.body.decode("UTF-8"))
    try:
        id = req.get("id")
        name = req.get("name")
        admin = req.get("admin")
        update_time = datetime.now()
        Group.objects.filter(id=id).update(name=name, admin=admin, update_time=update_time)
    except Exception as err:
        result = False
        message = str(err)
        return JsonResponse({"result": result, "code": 1, "message": message})
    else:
        result = True
        return JsonResponse({"result": result, "code": 0, "data": []})


def get_all_bk_users(request):
    """从蓝鲸平台，拉取所有用户列表"""
    try:
        client = get_client_by_request(request=request)
        response = client.usermanage.list_users()
    except Exception as err:
        # 请求接口失败
        result = False
        message = str(err)
        return JsonResponse({"result": result, "code": 1, "message": message})
    else:
        code = response.get("code")
        if code != 0:
            # 请求接口成功，但获取内容失败
            return response
        else:
            result = True
            return JsonResponse({"result": result, "code": 0, "data": response.get("data")})
