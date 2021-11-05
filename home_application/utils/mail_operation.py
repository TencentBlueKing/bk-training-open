#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2020-07-06 10:24:59
# @Remarks  :
import logging
import os

from blueking.component.shortcuts import get_client_by_user

logger = logging.getLogger(__name__)


def send_mail(receiver__username, title, content, body_format="Text", attachments=[]):
    """
    发邮件功能封装
    :param receiver__username:  接受用户的username
    :param title:               邮件标题
    :param content:             邮件内容
    :param body_format:         邮件格式，默认Text，也可选Html
    :param attachments:         邮件附件，格式与官方文档一致
    :return:                    API调用结果
    """
    # 从环境变量获取用户名(需添加白名单)
    user = os.getenv("BKAPP_API_INVOKE_USER")
    bk_client = get_client_by_user(user=user)
    # API请求参数
    kwargs = {
        "receiver__username": receiver__username,
        "title": title,
        "content": content,
        "body_format": body_format,
        "attachments": attachments,
    }
    send_result = bk_client.cmsi.send_mail(kwargs)
    if send_result["result"]:
        logger.info(send_result)
    else:
        error_info = {"邮件状态": "发送邮件失败", "邮件参数": kwargs, "返回结果": send_result}
        logger.error(error_info)
    return send_result
