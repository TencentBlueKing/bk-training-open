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
from home_application.models import Daily, Group, GroupUser, OffDay, User
from home_application.utils.report_operation import get_none_reported_user_of_group

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
    user = os.getenv("BKAPP_API_INVOKE_USER")  # noqa
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


def notify_admin_group_info(admin_username: str, group_infos: list, date: datetime.date):
    """
    告知管理员组内日报信息
    :param admin_username:  管理员的用户名
    :param date:            日报对应的日期
    :param group_infos:     该管理员管理的组信息list，每一包含组id、组名字、组管理员list
    :return:                发送邮件的返回值，即蓝鲸API调用结果
    """
    logger.info("定时任务：早上10点告知%s%s的日报信息: %s", admin_username, date, group_infos)
    date_str = date.strftime("%Y-%m-%d")

    # 组id-组name 对应关系
    group_id_name = {g_info["group_id"]: g_info["group_name"] for g_info in group_infos}

    # 组用户信息
    users = GroupUser.objects.filter(group_id__in=group_id_name.keys())
    user_ids = users.values_list("user_id", flat=True).distinct()
    user_infos = User.objects.filter(id__in=user_ids).values("id", "username", "name")
    user_usernames = user_infos.values_list("username", flat=True)

    # 用户-组 对应关系
    user_group_map = {}
    for user_info in user_infos:
        group_ids = users.filter(user_id=user_info["id"]).values_list("group_id", flat=True)
        user_group_map[user_info["username"]] = [group_id_name[gid] for gid in group_ids]

    # 用户日报渲染信息
    reports = Daily.objects.filter(date=date, create_by__in=user_usernames)
    report_data = [
        {
            "username": "{}({})".format(report.create_by, report.create_name),
            "group": " / ".join(user_group_map.get(report.create_by)),
            "content": report.content,
        }
        for report in reports
    ]

    # 已完成日报用户
    report_users = reports.values_list("create_by", flat=True)
    # 未完成日报用户
    none_report_users = user_infos.exclude(username__in=report_users)
    none_report_user_usernames = none_report_users.values_list("username", flat=True)

    # 请假用户
    off_day_usernames = OffDay.objects.filter(
        start_date__lte=date, end_date__gte=date, user__in=none_report_user_usernames
    ).values_list("user", flat=True)

    # 统计组内信息
    group_template_infos = []
    for g_info in group_infos:
        # 普通成员
        g_user_ids = users.filter(group_id=g_info["group_id"]).values_list("user_id", flat=True)
        g_user_usernames = user_infos.filter(id__in=g_user_ids).values_list("username", flat=True)
        simple_members = user_infos.filter(id__in=g_user_ids).exclude(username__in=g_info["admin_list"])
        # 请假人
        off_day_user = simple_members.filter(username__in=off_day_usernames)
        # 请假人username(name)
        off_day_user_format_name = " / ".join(
            [
                "{}({})".format(off_day_user_info["username"], off_day_user_info["name"])
                for off_day_user_info in off_day_user
            ]
        )
        # 没写日报的成员
        group_none_report_user = simple_members.filter(username__in=none_report_user_usernames).exclude(
            username__in=off_day_usernames
        )
        # 没写日报成员username(name)
        group_none_report_user_format_name = " / ".join(
            [
                "{}({})".format(group_none_report_user_info["username"], group_none_report_user_info["name"])
                for group_none_report_user_info in group_none_report_user
            ]
        )
        group_template_infos.append(
            {
                "group_id": g_info["group_id"],
                "group_name": g_info["group_name"],
                "daily_count": reports.filter(create_by__in=g_user_usernames)
                .exclude(create_by__in=g_info["admin_list"])
                .count(),
                "off_day_count": len(off_day_user),
                "off_day_user": off_day_user_format_name,
                "none_report_count": len(group_none_report_user),
                "none_report_user": group_none_report_user_format_name,
                "group_link": "{}manage-group?date={}&group={}".format(
                    settings.BKAPP_FULL_SITE_URL, date_str, g_info["group_id"]
                ),  # 组管理页面
            }
        )

    # 发送邮件
    mail_content = get_template("group_daily.html").render(
        {"date": date_str, "group_dailies": group_template_infos, "reports": report_data}
    )
    return send_mail(receiver__username=admin_username, title="日报信息查看", content=mail_content, body_format="Html")


def notify_report_info(report_date: datetime.date):
    """
    发送指定日期的日报概览给管理员
    :param report_date: 日报信息对应的日期
    """
    admin_group_map = {}  # 管理员管理的组
    # 查询所有组id 组名 组管理员
    group_name_and_admin = Group.objects.values("id", "name", "admin")
    # 构造管理员-组信息map，方便之后获取组信息
    for group_info in group_name_and_admin:
        admin_list = group_info["admin"].split(",")
        for admin_username in admin_list:
            if admin_username in admin_group_map.keys():
                admin_group_map[admin_username].append(
                    {"group_id": group_info["id"], "group_name": group_info["name"], "admin_list": admin_list}
                )
            else:
                admin_group_map[admin_username] = [
                    {"group_id": group_info["id"], "group_name": group_info["name"], "admin_list": admin_list}
                ]

    for admin_username, group_infos in admin_group_map.items():
        notify_admin_group_info(admin_username, group_infos, report_date)
    # 更新日报状态
    Daily.objects.filter(date=report_date).update(send_status=True, update_time=datetime.datetime.now())
    logger.info("%s的日报信息已发送给管理员" % report_date)
