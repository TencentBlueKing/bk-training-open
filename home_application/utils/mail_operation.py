#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2020-07-06 10:24:59
# @Remarks  : 邮件相关操作的封装
import logging
import os

from django.template.loader import get_template

from blueking.component.shortcuts import get_client_by_user

logger = logging.getLogger("celery")


def send_mail(receiver__username, title, content, body_format="Text", attachments=None):
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
    if attachments is None:
        attachments = []
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
        error_info = {"邮件状态": "发送邮件失败", "返回结果": send_result, "邮件参数": kwargs}
        logger.error(error_info)
    return send_result


def yesterday_report_notify(notify_title, notify_detail, button_text, button_link, receiver):
    """
    发送昨天的日报通知，适用成员的和管理员的
    :param notify_title:    通知标题
    :param notify_detail:   渲染通知内容的数据，数据格式为：
                            [
                                {"detail": "已完成：", "users": ["username(name)", "12345678Q(小乐乐)"]},
                                {"detail": "未完成：", "users": ["username(name)""]}
                            ]
    :param button_text:     按钮上显示的文字
    :param button_link:     点击按钮后的跳转链接
    :param receiver:        邮件接收人，由逗号分割的蓝鲸用户名，e.g. 123Q,456Q,789Q
    :return:                send_mail()方法的返回值
    """
    mail_content = get_template("yesterday_report.html").render(
        {
            "notify_title": notify_title,
            "notify_detail": notify_detail,
            "button_text": button_text,
            "button_link": button_link,
        }
    )
    return send_mail(
        receiver__username=receiver,
        title=notify_title,
        content=mail_content,
        body_format="Html",
    )
