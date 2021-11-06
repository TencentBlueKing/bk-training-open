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


def get_yesterday_reports():
    """
    获取昨天的日报内容
    """
    res = []

    # 查询所有组
    groups = Group.objects.all()
    groups_id = groups.values_list("id", flat=True)
    # 获取组相关的所有用户
    group_user = GroupUser.objects.filter(group_id__in=groups_id)
    # 获取这些用户的信息
    users = User.objects.filter(id__in=group_user.values_list("user_id", flat=True))
    # 获取日报信息
    yesterday = (datetime.datetime.today() - datetime.timedelta(days=1)).date()
    yesterday_reports = Daily.objects.filter(date=yesterday)
    # 按组获取各组日报内容
    for g in groups:
        # 存放组内用户的日报
        report_info = []
        # 组内成员信息
        group_members_id = group_user.filter(group_id=g.id).values_list("user_id", flat=True)
        group_members = users.filter(id__in=group_members_id)
        group_members_username = group_members.values_list("username", flat=True)

        # for循环: 获取组内日报信息
        for report in yesterday_reports.filter(create_by__in=group_members_username):
            report_user = group_members.get(username=report.create_by).name
            # 如果用户没有补充自己的真实姓名，则用username代替
            if not report_user:
                report_user = report.create_by

            report_info.append({"report_user": report_user, "report_content": report.content})
        # for循环结束

        res.append(
            {
                "group_name": g.name,
                "group_username": ",".join(list(group_members_username)),
                "group_reports": report_info,
            }
        )
    return res


def get_yesterday_not_report_user():
    """
    获取昨天没写日报的成员，然后告知管理员
    """
    # 查询所有组
    res = []
    groups = Group.objects.all()
    groups_id = groups.values_list("id", flat=True)
    # 获取组相关的所有用户
    group_user = GroupUser.objects.filter(group_id__in=groups_id)
    # 获取这些用户的信息
    users = User.objects.filter(id__in=group_user.values_list("user_id", flat=True))
    # 获取写了日报的用户
    yesterday = (datetime.datetime.today() - datetime.timedelta(days=1)).date()
    user_reported = Daily.objects.filter(date=yesterday).values_list("create_by")
    user_not_reported = users.exclude(username__in=user_reported)
    for g in groups:
        gid = g.id
        # 筛选组下没写日报的用户
        g_user = user_not_reported.filter(id__in=group_user.filter(group_id=gid).values_list("user_id", flat=True))
        if g_user.count() != 0:
            # 将所有没写日报的用户名字放到一个list里边
            username_not_reported = []
            for u in g_user:
                if u.name:
                    username_not_reported.append(u.name)
                else:
                    username_not_reported.append(u.username)
            res.append({"admins": g.admin, "group_name": g.name, "user_not_reported": username_not_reported})
    return res
