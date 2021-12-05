#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2021/11/2 17:42
# @Remarks  : 定时任务
import ast
import datetime
import logging

from celery.schedules import crontab
from celery.task import periodic_task, task
from django.template.loader import get_template

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
        logger.info("定时任务：每晚8点提醒没写日报的同学")
        notify_none_reported_user()


@periodic_task(run_every=crontab(minute=0, hour=10))
def morning_task():
    """
    每天早上10点发送前一天日报
    """
    today_date = datetime.date.today()
    today_info = CalendarHandler(today_date)
    if not today_info.is_holiday:
        logger.info("定时任务：每早10点告知管理员上一个工作日的日报情况")
        notify_yesterday_report_info(today_info.last_workday)


@task()
def send_daily_immediately(user_name, group_admins, daily_content, report_date, report_id):
    """
    TODO 更改为分管理员发送，用户补写日报后立刻发送给管理员
    :param user_name:       用户名：username(name)
    :param group_admins:    用户所在组的所有管理员
    :param daily_content:   日报内容，json数据
    :param report_date:     日报日期，str
    :param report_id:       日报id，用于发送后更新状态
    """
    mail_title = "日报补写提醒"
    mail_subhead = "您所管理的组有成员补写了『%s』的日报" % report_date
    group_reports = [
        {
            "report_user": user_name,
            "report_content": daily_content,
        }
    ]
    html_template = get_template("daily_report.html")
    mail_content = html_template.render(
        {"mail_title": mail_title, "mail_subhead": mail_subhead, "group_reports": group_reports}
    )
    send_res = send_mail(
        receiver__username=group_admins,
        title=mail_title,
        content=mail_content,
        body_format="Html",
    )
    if send_res["result"]:
        # 更新日报状态
        target_report = Daily.objects.get(id=report_id)
        target_report.send_status = True
        target_report.save()


@task()
def send_unfinished_dairy(user_name, date):
    """
    未完成日报提醒
    :param user_name: 用户名：username string(多人以逗号连接)
    :param date: 日期
    """

    mail_title = "{} 日报提醒".format(date)
    mail_content = "Hi，你还未完成{}的日报".format(date)

    send_mail(user_name, mail_title, mail_content)


@task()
def send_apply_for_group_to_manager(user_name, group_admins, group_name):
    """
    将申请入组请求发送给管理员
    :param user_name:       用户名：username(name)
    :param group_admins:    用户申请入组的所有管理员
    :param group_name:   组名
    """
    logger.info(
        "将申请入组请求发送给管理员 \n username: %s \n group_admins: %s \n group_name: %s", user_name, group_admins, group_name
    )
    mail_title = "申请入组请求"
    mail_content = "{}申请加入，您管理的组『{}』，快去处理吧~".format(user_name, group_name)
    send_mail(receiver__username=group_admins, title=mail_title, content=mail_content)


@task()
def send_good_daily(username, user_name, date, daily_list):
    """
    发送日报给组内所有人
    :param username: 管理员
    :param user_name: 用户名：username string(多人以逗号连接)
    :param date : 日报时间
    :param daily_list: 日报内容 日报评价
    """
    mail_title = "{} 日报推送".format(date)
    html_template = get_template("all_excellent.html")
    mail_content = html_template.render({"daily_list": daily_list, "username": username})
    send_mail(
        receiver__username=user_name,
        title=mail_title,
        content=mail_content,
        body_format="Html",
    )


@task()
def send_evaluate_daily(daily_id, evaluate_content):
    """
    将日报评价发生给个人
    :param daily_id:日报id
    :param evaluate_content: 日报内容
    """
    name = Daily.objects.filter(id=daily_id).values("create_name", "date", "content")
    username = User.objects.filter(name=name[0]["create_name"]).values("username")
    content = Daily.objects.filter(id=daily_id).values("content")
    content = ast.literal_eval(content[0]["content"])
    mail_title = "{} 日报评价".format(name[0]["date"])
    mail_content = "Hi，管理员已查看并评论你{}的日报".format(name[0]["date"])
    username = str(username[0]["username"])
    html_template = get_template("excellent.html")
    group_reports = [
        {
            "content": content,
            "username": username,
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
