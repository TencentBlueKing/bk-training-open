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


def data_to_table(table_style: str, data_style: str, data_list: list, data_count_every_row=3):
    """
    将数据构造成HTML邮件模板中的table
    :param table_style: table的css样式
    :param data_style: 单元格的css样式
    :param data_list: 数据列表
    :param data_count_every_row: table中每行元素的个数
    :return: 构造好的HTML代码
    """
    table_header = '<table class="%s">' % table_style
    table_end = "</table>"

    table_rows = []
    table_data = []
    for index in range(len(data_list)):
        table_data.append('<td class="{}">{}</td>'.format(data_style, data_list[index]))
        # 达到指定数量后构造一行table数据
        if (index + 1) % data_count_every_row == 0:
            table_rows.append("<tr>\n%s\n</tr>" % "\n".join(table_data))
            table_data.clear()
    # 检查table_data是否有遗漏
    if len(table_data) != 0:
        table_rows.append("<tr>\n%s\n</tr>" % "\n".join(table_data))
    table_body = "\n".join(table_rows)
    return "\n".join([table_header, table_body, table_end])
