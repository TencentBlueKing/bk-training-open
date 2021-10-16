#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2020-07-06 10:24:59
# @Remarks  : 包含home_application用到的所有装饰器
from django.http import JsonResponse

from home_application.models import Group


def is_group_admin(func):
    """
    需要具有对应组的管理员权限

    用法：需要将组id参数<group_id>放到url中
    urls.py写法参考：        path("report_template/<int:group_id>/", views.report_template),
    views.py写法参考：       def report_template(request, group_id):

    :param func: 被装饰的函数名
    :return: 经过views中响应逻辑函数处理后的http结果
    """

    def inner(request, group_id):
        """
        判断相关用户是否具有管理员权限
        :param group_id: 组id
        :param request: http请求体
        :return: 经过views中响应逻辑函数处理后的http结果
        """
        username = request.user.username
        try:
            temp_group = Group.objects.get(id=group_id)
            if username in temp_group.admin:
                return func(request, group_id)
            else:
                return JsonResponse({"result": False, "code": -1, "message": "没有相应组的管理权限", "data": []})
        except Group.DoesNotExist:
            return JsonResponse({"result": False, "code": -1, "message": "找不到对应的组，请核对组id", "data": []})

    return inner
