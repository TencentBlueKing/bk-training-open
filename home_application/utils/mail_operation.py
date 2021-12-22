#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2020-07-06 10:24:59
# @Remarks  : 邮件相关操作的封装
import datetime
import logging
import os

from celery.task import task
from django.template.loader import get_template

from blueapps.conf import settings
from blueking.component.shortcuts import get_client_by_user
from home_application.models import Daily, Group, OffDay
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
        off_day_list = OffDay.objects.filter(
            start_date__lte=datetime.date.today(), end_date__gte=datetime.date.today(), user__in=all_user_none_reported
        )
        all_user_none_reported = set(all_user_none_reported) - set(off_day_list)
    logger.info("定时任务：每晚8点提醒未写日报的用户：%s" % all_user_none_reported)
    remind_to_write_daily.apply_async(kwargs={"username_list": list(all_user_none_reported)})


@task()
def notify_admin_group_info(admin_username: str, group_infos: list, date=None):
    """
    告知管理员组内日报信息
    :param admin_username:  管理员的用户名
    :param date:            日报对应的日期，默认为昨天
    :param group_infos:     组信息list，具体数据格式如下：
                            [{
                                "group_name": 这是一个-很好听的名字, # 组名字
                                "daily_count": 10,              # 写了日报的人数
                                "none_write_daily_count": 1,    # 没写日报的人数，包含请假的人
                                "people_in_vacation_count": 0,  # 请假人数
                                "off_day_name_list":off_day_name_list,#请假人姓名
                                "group_link": settings.BKAPP_FULL_SITE_URL + "manage-group?date=2021-12-3&group=1"
                                  # 组管理页面
                            },]
    :return:                发送邮件的返回值，即蓝鲸API调用结果
    """
    if date is None:
        date = (datetime.datetime.today() - datetime.timedelta(days=1)).date()
    mail_content = get_template("group_daily.html").render(
        {
            "notify_title": "[{}] 日报速览".format(date),
            "group_dailies": group_infos,
        }
    )
    return send_mail(receiver__username=admin_username, title="日报提醒助手", content=mail_content, body_format="Html")


def notify_yesterday_report_info(report_date=None):
    """
    发送指定日期的日报概览给管理员
    :param report_date: 日报信息对应的日期，默认为昨天
    """
    admin_group_map = {}
    group_ids = Group.objects.values_list("id", flat=True)
    if report_date is None:
        report_date = (datetime.datetime.today() - datetime.timedelta(days=1)).date()
    report_date_str = report_date.strftime("%Y-%m-%d")
    for g_id in group_ids:
        # 组信息
        group_info = get_report_info_by_group_and_date(group_id=g_id, report_date=report_date)
        # 从组信息提取发送邮件需要的数据
        g_info_for_mail = {
            "group_name": group_info["name"],  # 组名字
            "daily_count": len(group_info["report_users"]),  # 写了日报的人数
            "none_write_daily_count": len(group_info["none_report_users"]),  # 没写日报的人数，包含请假的人
            "people_in_vacation_count": len(list(group_info["off_day_name_list"])),  # 请假人数
            "off_day_name_list": list(group_info["off_day_name_list"]),  # 请假人姓名列表
            "group_link": "{}manage-group?date={}&group={}".format(
                settings.BKAPP_FULL_SITE_URL, report_date_str, g_id
            ),  # 组管理页面
        }

        # 循环组内管理员，将组信息添到管理员管理的组信息中
        for admin_username in group_info["admin"]:
            if admin_username not in admin_group_map.keys():
                admin_group_map[admin_username] = []
            admin_group_map[admin_username].append(g_info_for_mail)

    logger.info("定时任务：工作日早10点告知管理员上个工作日的日报信息：%s" % admin_group_map)
    for admin_username, info in admin_group_map.items():
        notify_admin_group_info.apply_async(
            kwargs={
                "admin_username": admin_username,
                "group_infos": info,
                "date": report_date_str,
            }
        )
    # 更新日报状态
    Daily.objects.filter(date=report_date).update(send_status=True)
