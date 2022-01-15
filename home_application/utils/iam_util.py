#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2022/1/11 20:13
# @Remarks  : 这里封装日报系统需要用到的各种权限操作
import json
import logging

import requests
from iam import IAM, Action, Request, Resource, Subject

from blueapps.conf import settings
from home_application.models import Group

logger = logging.getLogger("component")


class IAMClient(object):
    def __init__(self):
        self.__iam = IAM(settings.APP_CODE, settings.SECRET_KEY, settings.BKAPP_IAM_HOST, settings.BK_URL)

    def __make_request_with_resources(self, username, action_id, resources):
        """
        判断用户是否具有指定资源(resources, 具体到示例，如日报系统的组)的指定权限(action_id)
        :param username: 目标用户名
        :param action_id: 操作id，如管理组的操作id为 'admin'
        :param resources: 要访问的资源
        :return: True: 可以访问; False: 无权限
        """
        request = Request(
            settings.BKAPP_IAM_SYSTEM_ID,
            Subject("user", username),
            Action(action_id),
            resources,
            None,
        )
        return request

    def __make_request_without_resources(self, username, action_id):
        request = Request(
            settings.BKAPP_IAM_SYSTEM_ID,
            Subject("user", username),
            Action(action_id),
            None,
            None,
        )
        return request

    def __grant_or_revoke_authority(self, username, group_id, group_name, bk_token, auth_type):
        """
        授权或者回收组管理权限
        :param username: 操作对象
        :param group_id: 组id        [注意] 这里组id和组名字都要传，不传会提示失败，而且要传之前保证两个的对应关系是正确的
        :param group_name: 组名字     [注意] 权限中心只会存储权限但是不会存储资源，所以权限中心无法判断两者之间的一致性
        :param bk_token: 当前用户登录态 TODO bk_token 与 bk_username 必须一个有效，bk_token 可以通过 Cookie 获取
        :param auth_type: 只能为grant(授权)或者revoke(回收权限)
        :return: True: 操作成功; False: 操作失败
        """
        # 下边的参数来自权限中心的官方文档 https://bk.tencent.com/docs/document/6.0/131/8449
        request_date = json.dumps(
            {
                "bk_app_code": settings.APP_CODE,
                "bk_app_secret": settings.SECRET_KEY,
                "bk_token": bk_token,
                "bk_username": settings.API_INVOKE_USER,
                "subject": {"type": "user", "id": username},
                "action": {"id": "admin"},
                "system": settings.BKAPP_IAM_SYSTEM_ID,
                "operate": auth_type,
                "asynchronous": False,
                "resources": [
                    {
                        "system": settings.BKAPP_IAM_SYSTEM_ID,
                        "type": "group",
                        "path": [{"type": "group", "id": group_id, "name": group_name}],
                    }
                ],
            }
        )
        url = "%s/api/c/compapi/v2/iam/authorization/path/" % settings.BK_URL
        response = requests.request("POST", url, data=request_date)

        if response.status_code != 200 or json.loads(response.text).get("code") != 0:
            if auth_type == "grant":
                auth_type_str = "授权失败"
            elif auth_type == "revoke":
                auth_type_str = "回收权限失败"
            else:
                auth_type_str = "未知的操作：%s" % auth_type
            logger.error(f"{auth_type_str}\r\n请求路由：{url}\r\n请求参数：{request_date}\r\n响应结果：{response.text}")
            return False
        else:
            return True

    def allowed_manage_group(self, username: str, group_id: int):
        """
        判断是否具有指定组的管理权限
        :param username: 用户名
        :param group_id: 组id
        :return:
        """
        # 这里对应的三个参数是权限中心注册的系统id、资源id、具体资源对象的id(这里是日报系统中的组id)，第四个参数未知
        r = Resource(settings.BKAPP_IAM_SYSTEM_ID, "group", str(group_id), {})
        resources = [r]
        request = self.__make_request_with_resources(username, "admin", resources)
        return self.__iam.is_allowed(request)

    def grant_admin_of_group(self, new_admin_username: str, group_id: int, group_name: str, cur_user_bk_token: str):
        """
        授权指定组的管理员权限
        :param new_admin_username: 新的管理员用户名
        :param group_id: 组id
        :param group_name: 组名字
        :param cur_user_bk_token: 当前登录用户的bk_token
        :return: True: 授权成功; False: 授权失败
        """
        return self.__grant_or_revoke_authority(new_admin_username, group_id, group_name, cur_user_bk_token, "grant")

    def revoke_admin_of_group(self, old_admin_username: str, group_id: int, group_name: str, cur_user_bk_token: str):
        """
        回收指定组指定管理员的权限
        :param old_admin_username: 当前管理员的用户名
        :param group_id: 组id    回收权限会根据组id回收，但是组名字也要传
        :param group_name: 组名字
        :param cur_user_bk_token: 当前登录用户的bk_token
        :return: True: 回收权限成功; False: 回收权限失败
        """
        return self.__grant_or_revoke_authority(old_admin_username, group_id, group_name, cur_user_bk_token, "revoke")

    def get_manage_group_list(self, username):
        """
        获取用户管理的所有组
        :param username: 目标用户名
        :return: 组信息list
        """
        request = self.__make_request_without_resources(username, "admin")

        # 注册的资源类型是group, 所以返回策略中是"group.id"
        # 但是数据库中对应的字段名是"id", 所以需要做个转换;
        key_mapping = {"group.id": "id"}

        # 默认make_filter使用的是DjangoQuerySetConverter，返回值是一个Q表达式
        filters = self.__iam.make_filter(request, key_mapping=key_mapping)

        # 如果从服务端查不到策略, 代表没有任何权限
        if not filters:
            return []
        # 直接用django queryset查
        groups = Group.objects.filter(filters).all()
        return [group.to_json() for group in groups]
