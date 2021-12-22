#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2020-07-06 10:24:59
# @Remarks  : 日报的相关处理
import datetime

from home_application.models import Daily, Group, GroupUser, OffDay, User


def content_format_as_json(daily_reports):
    """
    将查询到的日报内容格式化
    注意，这里针对日报QuerySet操作，单个日报可以直接调用to_json()方法
    :param daily_reports:   从数据库中查询到的QuerySet
    :return:                完全json格式化的日报内容
    """

    # 存放json格式化后的日报内容
    report_list = []
    for report in daily_reports:
        report_list.append(report.to_json())
    return report_list


def get_report_info_by_group_and_date(group_id: int, report_date=None):
    """
    获取指定日期指定组的日报信息
    :param group_id: 组id
    :param report_date: 日期，格式为2021-11-26，默认为昨天
    """
    if report_date is None:
        report_date = (datetime.datetime.today() - datetime.timedelta(days=1)).date()
    # 组
    group = Group.objects.get(id=group_id)
    # 组内管理员
    group_admin = group.admin_list
    # 组内用户
    group_user_ids = GroupUser.objects.filter(group_id=group_id).values_list("user_id", flat=True)
    group_users = User.objects.filter(id__in=group_user_ids)
    # 日报信息
    reports = Daily.objects.filter(date=report_date)
    report_users = group_users.filter(username__in=reports.values_list("create_by", flat=True)).exclude(
        username__in=group_admin
    )
    none_report_users = group_users.exclude(username__in=reports.values_list("create_by", flat=True)).exclude(
        username__in=group_admin
    )
    # 请假人列表
    off_day_username_list = OffDay.objects.filter(
        start_date__lte=datetime.date.today(),
        end_date__gte=datetime.date.today(),
        user__in=group_users.values_list("username", flat=True),
    ).values_list("user", flat=True)
    off_day_name_list = User.objects.filter(username__in=off_day_username_list).values_list("name", flat=True)
    # 返回数据
    return {
        "id": group.id,  # 组id
        "name": group.name,  # 组名
        "admin": group_admin,  # 组管理员数组
        "report_users": report_users,  # 已完成日报成员 [User(0), User(1), ···]
        "none_report_users": none_report_users,  # 未完成日报成员 [User(0), User(1), ···]
        "off_day_name_list": off_day_name_list,  # 请假成员姓名列表[崔, 王, ···]
        "reports": reports,  # 日报 [Daily(0), Daily(1), ···]
    }


def get_none_reported_user_of_group(group_id: int, date=None):
    """
    获取一个组里边没写日报的用户，管理员无需写日报
    :param group_id:    组id
    :param date:        日期，默认为今天
    :return:            用户名set
    """
    group = Group.objects.get(id=group_id)
    if date is None:
        date = datetime.datetime.today().date()
    # 成员列表
    member_ids = GroupUser.objects.filter(group_id=group_id).values_list("user_id", flat=True)
    member_usernames = User.objects.filter(id__in=member_ids).values_list("username", flat=True)
    # 写了日报的用户
    write_report_usernames = Daily.objects.filter(create_by__in=member_usernames, date=date).values_list(
        "create_by", flat=True
    )
    # 做差集得到没写日报的用户
    return set(member_usernames) - set(write_report_usernames) - set(group.admin_list)
