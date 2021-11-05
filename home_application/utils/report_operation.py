#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2020-07-06 10:24:59
# @Remarks  : 日报的相关处理


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
