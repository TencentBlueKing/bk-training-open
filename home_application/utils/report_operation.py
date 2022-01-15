#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2020-07-06 10:24:59
# @Remarks  : 日报的相关处理
import datetime

from home_application.models import Daily, Group, GroupUser, OffDay, User


def get_report_info_by_group_and_date(group_id: int, report_date: datetime.date):
    """
    获取指定日期指定组的日报信息
    :param group_id:    组id
    :param report_date: 日期
    """
    # 组
    group = Group.objects.get(id=group_id)
    # 组内管理员
    group_admin = group.admin_list
    # 所有成员
    group_user_ids = GroupUser.objects.filter(group_id=group_id).values_list("user_id", flat=True)
    group_users = User.objects.filter(id__in=group_user_ids)
    # 普通组员
    simple_users = group_users.exclude(username__in=group_admin)

    # 日报信息
    reports = Daily.objects.filter(date=report_date, create_by__in=group_users.values_list("username", flat=True))

    # 写日报的组员
    report_users = simple_users.filter(username__in=reports.values_list("create_by", flat=True))
    # 没写日报的组员(含请假)
    none_report_users = simple_users.exclude(username__in=report_users.values_list("username", flat=True))

    # 请假组员(不含请假但是写了日报的)
    off_day_username_list = OffDay.objects.filter(
        start_date__lte=report_date,
        end_date__gte=report_date,
        user__in=none_report_users.values_list("username", flat=True),
    ).values_list("user", flat=True)
    off_day_users = none_report_users.filter(username__in=off_day_username_list)

    # 没写日报且没请假组员
    none_report_users = none_report_users.exclude(username__in=off_day_users.values_list("username", flat=True))

    # 返回数据
    return {
        "id": group.id,  # 组id
        "name": group.name,  # 组名
        "admin_list": group_admin,  # 组管理员数组
        "report_users": report_users,  # 已完成日报成员 [User(0), User(1), ···]
        "none_report_users": none_report_users,  # 未完成日报成员 [User(0), User(1), ···]
        "off_day_users": off_day_users,  # 请假成员，不含请假但是写日报的 [User(0), User(1), ···]
        "reports": reports,  # 组内日报，包含管理员写的 [Daily(0), Daily(1), ···]
    }


def get_none_reported_user_of_group(group_id: int, date=None):
    """
    获取一个组里边没写日报的用户，管理员无需写日报 请假的无需写日报
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
    # 请假的用户
    off_day_list = OffDay.objects.filter(
        start_date__lte=datetime.date.today(), end_date__gte=datetime.date.today(), user__in=member_usernames
    ).values_list("user", flat=True)
    # 做差集得到没写日报的用户
    return set(member_usernames) - set(write_report_usernames) - set(group.admin_list) - set(off_day_list)
