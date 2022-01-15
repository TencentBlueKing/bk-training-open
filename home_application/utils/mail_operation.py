#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2020-07-06 10:24:59
# @Remarks  : 邮件相关操作的封装
import datetime
import logging
import time

from celery.task import task
from django.template.loader import get_template

from blueapps.conf import settings
from blueking.component.shortcuts import get_client_by_user
from home_application.models import Daily, Group
from home_application.utils.report_operation import (
    get_none_reported_user_of_group,
    get_report_info_by_group_and_date,
)

logger = logging.getLogger("celery")


def send_mail(receiver__username, title, content, body_format="Text", attachments=None):
    """
    发邮件功能封装
    :param receiver__username:  接受用户的username，多个用户就以","连接 e.g. 123Q,456Q,789Q
    :param title:               邮件标题
    :param content:             邮件内容
    :param body_format:         邮件格式，默认Text，也可选Html
    :param attachments:         邮件附件，格式与官方文档一致
    :return:                    API调用结果
    """
    # 从环境变量获取用户名(需添加白名单)
    if attachments is None:
        attachments = []
    user = settings.API_INVOKE_USER
    bk_client = get_client_by_user(user=user)
    # API请求参数
    kwargs = {
        "receiver__username": receiver__username,
        "title": title,
        "content": content,
        "body_format": body_format,
        "attachments": attachments,
    }
    # 发邮件前sleep 1秒，防止调用太频繁导致ESB挂掉
    time.sleep(1)
    send_result = bk_client.cmsi.send_mail(kwargs)
    if send_result["result"]:
        logger.info(send_result)
    else:
        error_info = {"邮件状态": "发送邮件失败", "返回结果": send_result, "邮件参数": kwargs}
        logger.error(error_info)
    return send_result


@task()
def remind_to_write_daily(username_list: list, date=None):
    """
    提醒指定用户写指定日期的日报
    :param username_list:   被提醒人用户名list
    :param date:            需要写日报的日期，默认为『今天』
    """
    if date is None:
        date = "今天"
    notify_content = "Hi, %s的日报还没完成，请" % date
    link_url = settings.BKAPP_FULL_SITE_URL
    link_text = "填写日报"

    mail_content = get_template("simple_notify.html").render(
        {"notify_title": "日报提醒", "notify_content": notify_content, "link_text": link_text, "link_url": link_url}
    )
    for username in username_list:
        send_mail(receiver__username=username, title="日报提醒助手", content=mail_content, body_format="Html")


def notify_none_reported_user():
    """
    每晚8点需要通知没写日报的用户及时写日报
    """
    all_user_none_reported = set()
    group_ids = Group.objects.values_list("id", flat=True)
    for group_id in group_ids:
        all_user_none_reported |= get_none_reported_user_of_group(group_id)
    logger.info("定时任务：每晚8点提醒未写日报的用户：%s" % all_user_none_reported)
    remind_to_write_daily.apply_async(kwargs={"username_list": list(all_user_none_reported)})


def notify_admin_group_info(group_id: int, date: datetime.date):
    """
    告知管理员组内日报信息
    :param group_id:        组id
    :param date:            日报日期
    :return:                发送邮件的返回值，即蓝鲸API调用结果
    """
    date_str = date.strftime("%Y-%m-%d")
    group_info = get_report_info_by_group_and_date(group_id, date)
    logger.info("定时任务：告知%s %s %s的日报信息", group_info["admin_list"], date, group_info["name"])
    # 发送邮件
    mail_content = get_template("daily_email.html").render(
        {
            "group_name": group_info["name"],
            "group_id": group_info["id"],
            "report_date": date_str,
            "reports": [report.to_json() for report in group_info["reports"]],
            "off_day_users": [{"username": user.username, "name": user.name} for user in group_info["off_day_users"]],
            "none_report_users": [
                {"username": user.username, "name": user.name} for user in group_info["none_report_users"]
            ],
            "bk_site_link": settings.BKAPP_FULL_SITE_URL,  # 网站根url
        }
    )
    return send_mail(
        receiver__username=",".join(group_info["admin_list"]),
        title="蓝鲸校园项目日报-{}-{}.{}.{}".format(group_info["name"], date.year, date.month, date.day),
        content=mail_content,
        body_format="Html",
    )


def notify_report_info(report_date: datetime.date):
    """
    发送指定日期的日报概览给管理员
    :param report_date: 日报信息对应的日期
    """
    # 查询所有组id 组名 组管理员
    group_ids = Group.objects.values_list("id", flat=True)
    for gid in group_ids:
        notify_admin_group_info(gid, report_date)
    # 更新日报状态
    Daily.objects.filter(date=report_date).update(send_status=True, update_time=datetime.datetime.now())
    logger.info("%s的日报信息已发送给管理员" % report_date)
