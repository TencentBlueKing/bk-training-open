#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2022/1/10 12:49
# @Remarks  : 权限中心的相关操作
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from blueapps.account.decorators import login_exempt
from blueapps.conf import settings
from home_application.models import Group


@login_exempt
@csrf_exempt
@require_POST
def group(request):
    """拉取组信息"""
    req = json.loads(request.body)
    # 鉴权
    token_b64 = request.META.get("HTTP_AUTHORIZATION")
    if token_b64 is None or token_b64 != settings.BKAPP_IAM_AUTH_TOKEN:
        return JsonResponse({"code": 401, "message": "权限认证失败", "data": {}})

    allowed_method = ["list_instance", "search_instance"]  # 允许的拉取方式
    allowed_type = ["group"]  # 允许拉取的资源

    method = req.get("method")
    resource_type = req.get("type")
    query_page = req.get("page")

    # 判断资源、拉取方式是否合法
    if not (method in allowed_method and resource_type in allowed_type):
        return JsonResponse({"code": 404, "message": "不存在的资源信息查询方式，请核对", "data": {}})

    # 查询组信息
    if method == "search_instance":
        # 如果是搜索则需要根据keyword筛选，搜索不区分大小写
        keyword = req["filter"]["keyword"]
        groups = Group.objects.filter(name__icontains=keyword).values("id", "name")
    else:
        groups = Group.objects.values("id", "name")

    # 根据page参数切片
    offset_start = query_page["offset"]
    offset_end = offset_start + query_page["limit"]
    group_infos = [
        {"id": group_info["id"], "display_name": group_info["name"]} for group_info in groups[offset_start:offset_end]
    ]

    # 返回数据
    return JsonResponse({"code": 0, "message": "success", "data": {"count": groups.count(), "results": group_infos}})
