#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2022/1/14 17:01
# @Remarks  : 组相关通用操作
from home_application.utils.iam_util import IAMClient


def update_group_admins(old_admins: list, new_admins: list, group_id: int, group_name: str, bk_token: str):
    # 在权限中心给管理员赋权
    iam_client = IAMClient()

    old_admins_set = set(old_admins)
    new_admins_set = set(new_admins)

    to_remove_admins = list(old_admins_set - new_admins_set)  # 待移除管理员
    to_add_admins = list(new_admins_set - old_admins_set)  # 待添加管理员

    # 赋权
    while len(to_add_admins) != 0:
        admin_username = to_add_admins[0]
        if iam_client.grant_admin_of_group(admin_username, group_id, group_name, bk_token):
            to_add_admins.pop(0)
            old_admins.append(admin_username)
        else:
            # 如果在赋权时失败（权限中心挂了）就直接返回
            break
    # 回收权限
    while len(to_remove_admins) != 0:
        admin_username = to_remove_admins[0]
        if iam_client.revoke_admin_of_group(admin_username, group_id, group_name, bk_token):
            to_remove_admins.pop(0)
            old_admins.remove(admin_username)
        else:
            # 如果在回收权限时失败（权限中心挂了）就直接返回
            break
    return old_admins
