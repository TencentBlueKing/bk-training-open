#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2021/12/2 14:00
# @Remarks  : 日历处理操作
import datetime

from home_application.models import Holiday


class CalendarHandler:

    date: datetime.date

    _is_initialized = False  # 标记是否已经查询过数据库获取日期信息
    _is_holiday: bool  # 存储是否节假日信息，只有在查询过数据库之后才会被赋值
    _note: str  # 存储日期信息备注，只有在查询过数据库之后才会被赋值

    def __init__(self, target_date: datetime.date):
        """
        根据日期初始化
        """
        self.date = target_date

    def __str__(self):
        return "{}年{}月{}日".format(self.year, self.month, self.day)

    @property
    def year(self):
        return self.date.year

    @property
    def month(self):
        return self.date.month

    @property
    def day(self):
        return self.date.day

    def _get_day_info(self):
        try:
            holiday_info = Holiday.objects.get(year=self.year, month=self.month, day=self.day)
            self._is_holiday = holiday_info.is_holiday
            self._note = holiday_info.note
        except Holiday.DoesNotExist:
            # 找不到就根据周六周日判断
            self._is_holiday = self.date.isoweekday() > 5
            if self._is_holiday:
                self._note = "周末"
            else:
                self._note = "工作日"
        self._is_initialized = True

    @property
    def is_holiday(self):
        """
        判断当前日期是否为节假日
        """
        if not self._is_initialized:
            self._get_day_info()
        return self._is_holiday

    @property
    def note(self):
        """
        获取当前日期的备注
        """
        if not self._is_initialized:
            self._get_day_info()
        return self._note

    @property
    def last_workday(self):
        """
        获取上一个工作日
        """
        res_date = None

        # 首先在当前月查询，查询不到就查询上一个月
        cur_year = self.year  # 当前查询年份
        cur_month = self.month  # 当前查询月份
        cur_date = self.date - datetime.timedelta(days=1)

        while res_date is None:
            # 获取一个月的法定节假日和调休的工作日，如果找不到就往上个月查找
            holiday_infos = Holiday.objects.filter(year=cur_year, month=cur_month)

            # ↓↓↓ 内层while开始：尝试在当前月查找工作日
            while cur_month == cur_date.month:
                try:
                    # 先查找数据库
                    temp_holiday_info = holiday_infos.get(year=cur_date.year, month=cur_date.month, day=cur_date.day)
                    if not temp_holiday_info.is_holiday:
                        res_date = cur_date
                        break
                except Holiday.DoesNotExist:
                    # 数据库中没有就根据周几来判断
                    if cur_date.isoweekday() <= 5:
                        res_date = cur_date
                        break
                # 如果不是则往前查一天
                cur_date = cur_date - datetime.timedelta(days=1)
            # ↑↑↑ 内层while结束

            # 当月没有工作日就查询上个月
            cur_year = cur_date.year
            cur_month = cur_date.month
        return res_date
