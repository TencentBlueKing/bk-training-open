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

from home_application.models import Daily, Group, User
from home_application.utils.get_people_for_mail_notify import (
    get_people_not_reported,
    get_report_info_by_group_and_date,
)
from home_application.utils.mail_operation import send_mail, yesterday_report_notify
from home_application.utils.report_operation import data_to_table

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
    all_group_ids = Group.objects.values_list("id", flat=True)

    for group_id in all_group_ids:
        # 获取组内日报信息
        group_report_info = get_report_info_by_group_and_date(group_id)

        # 组员=写日报的+没写日报的-管理员
        report_user_username = set(group_report_info["report_users"].values_list("username", flat=True))
        none_report_username = set(group_report_info["none_report_users"].values_list("username", flat=True))
        admin_username = set(group_report_info["admin"])
        member_username = ",".join((report_user_username | none_report_username) - admin_username)

        notify_title = "{}『{}』日报一览：".format(yesterday_date_str, group_report_info["name"])
        notify_detail = []

        # 发送组员的日报邮件
        if len(group_report_info["report_users"]) != 0:
            users_html_table = data_to_table(
                table_style="mail_body",
                data_style="center_style",
                data_list=["{}({})".format(user.username, user.name) for user in group_report_info["report_users"]],
            )
            notify_detail.append(
                {
                    "detail": "已完成：",
                    "users_table": users_html_table,
                }
            )
            yesterday_report_notify(
                notify_title=notify_title,
                notify_detail=notify_detail,
                button_text="点击查看详情",
                button_link="https://paas-edu.bktencent.com/t/train-test/groupDailys?date={}&group={}".format(
                    yesterday_date_str, group_report_info["id"]
                ),
                receiver=member_username,
            )

        # 发送管理员的日报邮件
        users_html_table = data_to_table(
            table_style="mail_body",
            data_style="center_style",
            data_list=["{}({})".format(user.username, user.name) for user in group_report_info["none_report_users"]],
        )
        notify_detail.append({"detail": "未完成：", "users_table": users_html_table})
        send_res = yesterday_report_notify(
            notify_title=notify_title,
            notify_detail=notify_detail,
            button_text="点击查看详情",
            button_link="https://paas-edu.bktencent.com/t/train-test/manageGroup?date={}&group={}".format(
                yesterday_date_str, group_report_info["id"]
            ),
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
def send_good_daily(user_name, date, content_list, evaluate_name):
    """
    发生日报给组内所有人
    :param user_name: 用户名：username string(多人以逗号连接)
    :param date : 日报时间
    :param content_list: 日报内容
    :param evaluate_name:日报评价
    """
    content_list_dict = []
    for content_list in content_list:
        content_list = ast.literal_eval(content_list)
        content_list_dict.append(content_list)
    mail_title = "{} 日报推送".format(date)
    html_template = get_template("all_excellent.html")
    zip_data = zip(content_list_dict, evaluate_name)
    mail_content = html_template.render({"zip_data": zip_data})
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
