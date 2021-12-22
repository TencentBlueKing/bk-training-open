#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2021/11/2 17:42
# @Remarks  : 定时任务
import datetime
import logging

from celery.schedules import crontab
from celery.task import periodic_task, task
from django.template.loader import get_template

from blueapps.conf import settings
from home_application.models import Daily, User
from home_application.utils.calendar_util import CalendarHandler
from home_application.utils.mail_operation import (
    notify_none_reported_user,
    notify_yesterday_report_info,
    send_mail,
)

logger = logging.getLogger("celery")


@periodic_task(run_every=crontab(minute=0, hour=20))
def evening_task():
    """
    每天晚上8点发送提醒邮件
    """
    today = datetime.date.today()
    if not CalendarHandler(today).is_holiday:
        notify_none_reported_user()


@periodic_task(run_every=crontab(minute=0, hour=10))
def morning_task():
    """
    每天早上10点发送前一天日报
    """
    today_date = datetime.date.today()
    today_info = CalendarHandler(today_date)
    if not today_info.is_holiday:
        notify_yesterday_report_info(today_info.last_workday)


@task()
def send_apply_for_group_to_manager(user_name, group_admins, group_name, group_id):
    """
    将申请入组请求发送给管理员
    :param user_name:       用户名：username(name)
    :param group_admins:    用户申请入组的所有管理员(邮件接收人)
    :param group_name:   组名
    :param group_id:    组id
    """
    logger.info(
        "将申请入组请求发送给管理员 \n username: %s \n group_admins: %s \n group_name: %s \n group_id: %s",
        user_name,
        group_admins,
        group_name,
        group_id,
    )
    mail_title = "申请入组请求"
    link_text = "点击查看"
    link_url = "%smanage-group?group={}".format(group_id) % settings.BKAPP_FULL_SITE_URL  # 组管理页面
    mail_content = get_template("simple_notify.html").render(
        {
            "notify_title": mail_title,
            "notify_content": "{}申请加入您管理的组『{}』，快去处理吧~".format(user_name, group_name),
            "link_text": link_text,
            "link_url": link_url,
        }
    )
    send_mail(receiver__username=group_admins, title=mail_title, content=mail_content, body_format="Html")


@task()
def send_apply_for_group_result(username, group_name, status):
    """
    将申请入组请求发送给管理员
    :param username:        用户名：username(邮件接收人)
    :param group_name       组名
    :param status:          处理结果：status=1(同意)、status=2(拒绝)
    """
    logger.info(
        "将申请入组请求处理结果发送用户 \n username: %s \n group_name: %s \n status(status=1同意、status=2拒绝): %s",
        username,
        group_name,
        status,
    )
    title = "申请入组请求处理结果"
    if status == 1:
        content = "您的申请入组『{}』请求被管理员通过~".format(group_name)
    else:
        content = "很遗憾，您的申请入组『{}』请求被管理员拒绝".format(group_name)
    mail_content = get_template("simple_notify.html").render({"notify_title": title, "notify_content": content})
    send_mail(receiver__username=username, title=title, content=mail_content, body_format="Html")


@task()
def send_good_daily(evaluate_name, user_name, date, daily_list):
    """
    发送日报给组内所有人
    :param evaluate_name: 管理员
    :param user_name: 用户名：username string(多人以逗号连接)
    :param date : 日报时间
    :param daily_list: 日报内容 日报评价
    """
    mail_title = "{} 日报推送".format(date[0:10])
    html_template = get_template("all_excellent.html")
    mail_content = html_template.render({"daily_list": daily_list, "evaluate_name": evaluate_name, "date": date[0:10]})
    send_mail(
        receiver__username=user_name,
        title=mail_title,
        content=mail_content,
        body_format="Html",
    )


@task()
def send_evaluate_daily(evaluate_name, daily_id, evaluate_content):
    """
    将日报评价发生给个人
    :param daily_id:日报id
    :param evaluate_content: 日报内容
    :param evaluate_name :评价人姓名
    """
    name = Daily.objects.filter(id=daily_id).values("create_name", "date", "content")
    username = User.objects.filter(name=name[0]["create_name"]).values("username")
    content = Daily.objects.filter(id=daily_id).values("content")
    content = content[0]["content"]
    mail_title = "{} 日报评价".format(name[0]["date"])
    mail_content = "Hi，管理员已查看并评论你{}的日报".format(name[0]["date"])
    username = str(username[0]["username"])
    html_template = get_template("excellent.html")
    group_reports = [
        {
            "content": content,
            "evaluate_name": evaluate_name,
            "evaluate_content": evaluate_content,
        }
    ]
    mail_content = html_template.render(
        {"mail_title": mail_title, "mail_content": mail_content, "group_reports": group_reports}
    )
    send_mail(
        receiver__username=username,
        title=mail_title,
        content=mail_content,
        body_format="Html",
    )
