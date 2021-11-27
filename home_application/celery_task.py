#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2021/11/2 17:42
# @Remarks  : 定时任务
import datetime
import logging

from celery.schedules import crontab
from celery.task import periodic_task, task
from django.template.loader import get_template

from home_application.models import Daily
from home_application.utils.get_people_for_mail_notify import (
    get_people_not_reported,
    get_yesterday_not_report_user,
    get_yesterday_reports,
)
from home_application.utils.mail_operation import send_mail

logger = logging.getLogger("celery")


@periodic_task(run_every=crontab(minute=0, hour=20))
def remind_to_write_daily():
    """
    每天晚上8点发送提醒邮件
    """
    logger.info("定时任务：每晚8点提醒没写日报的同学")
    user_to_notified = ",".join(get_people_not_reported())
    # 都写了日报则无需处理
    if not user_to_notified:
        return
    html_template = get_template("simple_notify.html")
    mail_content = html_template.render(
        {
            "notify_title": "日报提醒",
            "notify_content": "Hi,你今天还写日报，是不是忘记？快来写吧",
            "button_text": "点我去写日报",
            "button_link": "https://paas-edu.bktencent.com/t/train-test/",
        }
    )
    send_mail(receiver__username=user_to_notified, title="日报提醒助手", content=mail_content, body_format="Html")


def notify_admin_who_not_reported():
    """
    告知管理员组内哪些人没写日报
    """
    logger.info("定时任务：每早10点告知管理员昨天没写日报的用户")
    not_reported = get_yesterday_not_report_user()
    for mail_info in not_reported:
        html_template = get_template("simple_notify.html")
        notify_content = "您所管理的组『{}』内以下成员昨天没写日报，请留意：\n\n{}".format(
            mail_info["group_name"], ", ".join(mail_info["user_not_reported"])
        )
        mail_content = html_template.render(
            {"notify_title": "日报提醒", "notify_content": notify_content, "button_text": None, "button_link": None}
        )
        mail_title = "昨日未写日报用户(%s)" % mail_info["group_name"]
        send_mail(receiver__username=mail_info["admins"], title=mail_title, content=mail_content, body_format="Html")


@periodic_task(run_every=crontab(minute=0, hour=10))
def send_yesterday_report():
    """
    每天早上10点发送前一天日报，同时告知管理员组内那些同学没交日报
    """
    logger.info("定时任务：每早10点发送前一天所有人的日报")
    yesterday_date = datetime.datetime.today() - datetime.timedelta(days=1)
    notify_info = get_yesterday_reports()

    # 分组发送各组的日报
    for group_info in notify_info:
        group_name = group_info["group_name"]
        group_username = group_info["group_username"]

        if len(group_info["group_reports"]) != 0:
            html_template = get_template("daily_report.html")
            mail_content = html_template.render(
                {
                    "mail_title": "昨天日报信息速览",
                    "mail_subhead": "『%s』昨天的日报情况如下:" % group_name,
                    "group_reports": group_info["group_reports"],
                }
            )
        else:
            html_template = get_template("simple_notify.html")
            mail_content = html_template.render(
                {
                    "notify_title": "昨天日报信息",
                    "notify_content": "你所在组『%s』，昨天没人写日报，今天要加油啊！" % group_name,
                    "button_text": None,
                    "button_link": None,
                }
            )
        send_res = send_mail(
            receiver__username=group_username,
            title="{}的日报({})".format(str(yesterday_date.date()), group_name),
            content=mail_content,
            body_format="Html",
        )
        if send_res["result"]:
            ids = group_info["group_reports_id"]
            Daily.objects.filter(id__in=ids).update(send_status=True)
    # 然后告知管理员昨天没写日报的用户
    notify_admin_who_not_reported()


@task()
def send_daily_immediately(user_name, group_admins, daily_content, report_date, report_id):
    """
    用户补写日报后立刻发送给管理员
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
