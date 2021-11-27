#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2021/11/2 17:42
# @Remarks  : 定时任务
import datetime
import logging

from celery.schedules import crontab
from celery.task import periodic_task, task
from django.template.loader import get_template

from home_application.models import Daily, Group
from home_application.utils.get_people_for_mail_notify import (
    get_people_not_reported,
    get_report_info_by_group_and_date,
)
from home_application.utils.mail_operation import send_mail, yesterday_report_notify

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


def send_yesterday_report():
    """
    发送昨天的日报邮件
    """
    yesterday_date_str = str((datetime.datetime.today() - datetime.timedelta(days=1)).date())
    # 遍历所有组发邮件
    all_groups = Group.objects.all()

    for group in all_groups:
        # 获取组内日报信息
        group_report_info = get_report_info_by_group_and_date(group.id)
        # 组员=写日报的+没写日报的-管理员
        report_user_username = set(group_report_info["report_users"].values_list("username", flat=True))
        member_username = ",".join(
            report_user_username.union(
                set(group_report_info["none_report_users"].values_list("username", flat=True))
            ).difference(set(group_report_info["admin"]))
        )
        notify_title = "{}『{}』日报一览：".format(yesterday_date_str, group_report_info["name"])
        notify_detail = []

        # 发送组员的日报邮件
        if len(group_report_info["report_users"]) != 0:
            notify_detail.append(
                {"detail": "已完成：", "users": {item.username: item.name for item in group_report_info["report_users"]}}
            )
            yesterday_report_notify(
                notify_title=notify_title,
                notify_detail=notify_detail,
                button_text="点击查看详情",
                button_link="https://paas-edu.bktencent.com/t/train-test/groupDailys?date=%s&group=%s"
                % (yesterday_date_str, group_report_info["id"]),
                receiver=member_username,
            )

        # 发送管理员的日报邮件
        notify_detail.append(
            {"detail": "未完成：", "users": {item.username: item.name for item in group_report_info["none_report_users"]}}
        )
        send_res = yesterday_report_notify(
            notify_title=notify_title,
            notify_detail=notify_detail,
            button_text="点击查看详情",
            button_link="https://paas-edu.bktencent.com/t/train-test/manageGroup?date=%s&group=%s"
            % (yesterday_date_str, group_report_info["id"]),
            receiver=",".join(group_report_info["admin"]),
        )
        # 更新日报状态为已发送
        if send_res["result"]:
            Daily.objects.filter(date=yesterday_date_str, create_by__in=report_user_username).update(send_status=True)


@periodic_task(run_every=crontab(minute=0, hour=10))
def morning_task():
    """
    每天早上10点发送前一天日报
    """
    logger.info("定时任务：每早10点发送前一天所有人的日报")
    send_yesterday_report()


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
