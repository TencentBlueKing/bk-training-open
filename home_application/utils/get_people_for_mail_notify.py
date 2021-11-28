#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2020-07-06 10:24:59
# @Remarks  :
import datetime

from home_application.models import Daily, Group, GroupUser, User


def get_people_not_reported():
    """
    获取所有今天还没有发日报的用户
    """
    # 获取今天已经发了日报的用户
    people_reported = Daily.objects.filter(date=datetime.date.today()).values_list("create_by", flat=True)
    # 筛选今天还没有发日报的用户
    return list(User.objects.exclude(username__in=people_reported).values_list("username", flat=True))


def get_report_info_by_group_and_date(group_id: int, report_date=None):
    """
    获取指定日期指定组的日报信息
    :param report_date: 日期，格式为2021-11-26，默认为昨天
    :param group_id: 组id
    """
    if report_date is None:
        report_date = (datetime.datetime.today() - datetime.timedelta(days=1)).date()
    # 组
    group = Group.objects.get(id=group_id)
    # 组内用户
    group_user_ids = GroupUser.objects.filter(group_id=group_id).values_list("user_id", flat=True)
    group_users = User.objects.filter(id__in=group_user_ids)
    # 日报信息
    reports = Daily.objects.filter(date=report_date)
    report_users = group_users.filter(username__in=reports.values_list("create_by", flat=True))
    none_report_users = group_users.exclude(username__in=reports.values_list("create_by", flat=True))
    # 返回数据
    return {
        "id": group.id,  # 组id
        "name": group.name,  # 组名
        "admin": group.admin_list,  # 组管理员数组
        "report_users": report_users,  # 已完成日报成员 [User(0), User(1), ···]
        "none_report_users": none_report_users,  # 未完成日报成员 [User(0), User(1), ···]
        "reports": reports,  # 日报 [Daily(0), Daily(1), ···]
    }
