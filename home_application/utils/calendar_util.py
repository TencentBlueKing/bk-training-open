#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2021/12/2 14:00
# @Remarks  : 日历处理操作
import datetime

from home_application.models import Holiday


def date_valid(year: int, month: int, day: int):
    """
    核对日期是否合法
    :param year: 年份
    :param month: 月份
    :param day: 日期
    :return: True or False
    """
    if year < 1900:
        return False
    month_31 = {1, 3, 5, 7, 8, 10, 12}
    month_30 = {4, 6, 9, 11}
    if month in month_31:
        return 1 <= day <= 31
    elif month in month_30:
        return 1 <= day <= 30
    elif month == 2:
        is_leap_year = (year % 4 == 0 and year % 100 != 0) or year % 400 == 0
        return 1 <= day <= 28 or (is_leap_year and day == 29)
    return False


def get_last_month(cur_year: int, cur_month: int):
    """
    获取上个月份及其对应的年份
    :param cur_year: 当前年份
    :param cur_month: 当前月份
    :return: 返回两个值，年和月
    """
    if cur_month == 1:
        return cur_year - 1, 12
    else:
        return cur_year, cur_month - 1


class CalendarHandler:
    _year: int
    _month: int
    _day: int
    _is_holiday: bool
    _note: str

    _day_info: Holiday

    # ↓↓↓构造方法--------------------------------------------------------------------------------------
    def __init__(self, year, month, day):
        """
        指定年月日构造日历工具
        :param year:    年份
        :param month:   月份
        :param day:     日期
        """
        self._get_day_info(year, month, day)

    @classmethod
    def today(cls):
        today = datetime.datetime.today()
        return cls(today.year, today.month, today.day)

    @classmethod
    def by_datetime(cls, date_time: datetime.datetime):
        return cls(date_time.year, date_time.month, date_time.day)

    @classmethod
    def by_date(cls, target_date: datetime.date):
        return cls(target_date.year, target_date.month, target_date.day)

    # ↑↑↑构造方法--------------------------------------------------------------------------------------

    def __str__(self):
        return "{}年{}月{}日 {}".format(self._year, self._month, self._day, self._note)

    def _get_day_info(self, year: int, month: int, day: int):
        if not date_valid(year, month, day):
            raise ValueError("不合法的日期")

        self._year = year
        self._month = month
        self._day = day

        try:
            holiday_info = Holiday.objects.get(year=self._year, month=self._month, day=self._day)
            self._is_holiday = holiday_info.is_holiday
            self._note = holiday_info.note
        except Holiday.DoesNotExist:
            # 找不到就根据周六周日判断
            self._is_holiday = datetime.datetime(year=self._year, month=self._month, day=self._day).isoweekday() > 5
            if self._is_holiday:
                self._note = "周末"
            else:
                self._note = "工作日"

    @property
    def is_workday(self):
        """
        判断当前日期是否为工作日
        """
        return not self._is_holiday

    @property
    def last_workday(self):
        """
        获取上一个工作日
        """
        res_date = None
        # 首先在当前月查询，查询不到就查询上一个月
        cur_year = self._year  # 当前查询年份
        cur_month = self._month  # 当前查询月份
        cur_date = datetime.date(self._year, self._month, self._day) - datetime.timedelta(days=1)
        while res_date is None:
            # 获取指定月的法定节假日和调休的工作日
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
            cur_year, cur_month = get_last_month(cur_year, cur_month)
        return res_date
