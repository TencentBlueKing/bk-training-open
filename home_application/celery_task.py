#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2021/11/2 17:42
# @Remarks  : 定时任务
import datetime
import logging

from celery.schedules import crontab
from celery.task import periodic_task

from home_application.utils.get_people_for_mail_notify import (
    get_people_not_reported,
    get_yesterday_reports,
)
from home_application.utils.mail_operation import send_mail

logger = logging.getLogger(__name__)


# 每天晚上8点发送提醒邮件
@periodic_task(run_every=crontab(minute=0, hour=20))
def remind_to_write_daily():
    logger.info("定时任务：每晚8点提醒没写日报的同学")
    user_to_notified = ",".join(get_people_not_reported())
    send_mail(receiver__username=user_to_notified, title="日报提醒助手", content="你好，你今天的日报还没有写，快去写日报吧")


# 每天早上10点发送前一天日报
@periodic_task(run_every=crontab(minute=0, hour=10))
def send_yesterday_report():
    logger.info("定时任务：每早10点发送前一天所有人的日报")
    yesterday_date = datetime.datetime.today() - datetime.timedelta(days=1)
    notify_info = get_yesterday_reports()
    for group_info in notify_info:
        group_name = group_info["group_name"]
        group_username = group_info["group_username"]
        # 下边拼接日报内容成字符串
        group_reports = ""
        for report_info in group_info["group_reports"]:
            group_reports += report_info["report_user"] + "\n"
            group_reports += str(report_info["report_content"]) + "\n"
        if len(group_reports) == 0:
            group_reports = "昨天没人写日报，今天加油！"
        # 分组发送各组的日报
        send_mail(
            receiver__username=group_username,
            title="{}的日报({})".format(str(yesterday_date.date()), group_name),
            content=group_reports,
        )
