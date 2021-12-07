# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import ast

from django.db import models
from django_mysql.models import JSONField


# Create your models here.
# 创建时间和更新时间基类
class TimeBasic(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        abstract = True


# 组
class Group(TimeBasic):
    name = models.CharField(max_length=128, unique=True, verbose_name="组名字")
    # 逗号分隔，一个或多个管理员用户名拼接成的字符串
    admin = models.CharField(max_length=255, verbose_name="管理员们")
    create_by = models.CharField(max_length=128, verbose_name="创建人")
    create_name = models.CharField(max_length=128, verbose_name="创建人姓名")

    def __str__(self):
        return self.name

    @property
    def admin_list(self):
        return self.admin.split(",")

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "admin": self.admin,
            "create_by": self.create_by,
            "create_name": self.create_name,
        }


# 组中的日报通知人
class GroupNotifier(models.Model):
    group_id = models.IntegerField(verbose_name="组id")
    daily_notifier_id = models.IntegerField(verbose_name="日报通知人")

    def __str__(self):
        return "组id是：" + str(self.group_id) + " 日报通知人id：" + str(self.daily_notifier_id)

    class Meta:
        unique_together = ("group_id", "daily_notifier_id")


# 用户表
class User(TimeBasic):
    username = models.CharField(max_length=128, unique=True, verbose_name="用户账号")
    name = models.CharField(max_length=128, null=True, blank=True, verbose_name="用户姓名")
    phone = models.CharField(max_length=30, null=True, blank=True, verbose_name="电话号码")
    email = models.EmailField(null=True, blank=True, verbose_name="邮箱")

    def __str__(self):
        return self.username


# 组-用户关联表
class GroupUser(models.Model):
    group_id = models.IntegerField(verbose_name="组id")
    user_id = models.IntegerField(verbose_name="用户id")

    def __str__(self):
        return "组id：" + str(self.group_id) + " 用户id：" + str(self.user_id)

    class Meta:
        unique_together = ("group_id", "user_id")


# 申请入组表
class ApplyForGroup(TimeBasic):
    group_id = models.IntegerField(verbose_name="组id")
    user_id = models.IntegerField(verbose_name="用户id")
    operator = models.IntegerField(null=True, verbose_name="处理人id")
    status = models.SmallIntegerField(verbose_name="申请状态")

    def __str__(self):
        return "组id：" + str(self.group_id) + " 用户id：" + str(self.user_id)


# 日报模板表
class DailyReportTemplate(models.Model):
    name = models.CharField(max_length=128, verbose_name="日报模板名字")
    content = models.CharField(max_length=255, verbose_name="日报模板内容")
    create_by = models.CharField(max_length=128, verbose_name="创建人")
    create_name = models.CharField(max_length=128, verbose_name="创建人姓名")
    group_id = models.IntegerField(verbose_name="组id")

    def __str__(self):
        return self.name


def daily_evaluate_default():
    return []

def daily_content_default():
    return []


# 日报表
class Daily(TimeBasic):
    content = JSONField(verbose_name="日报内容", default=daily_content_default)
    create_by = models.CharField(max_length=128, verbose_name="创建人")
    create_name = models.CharField(max_length=128, verbose_name="创建人姓名")
    date = models.DateField(verbose_name="日报日期")
    send_status = models.BooleanField(verbose_name="发送状态", default=False)
    template_id = models.IntegerField(verbose_name="模板id")
    evaluate = JSONField(verbose_name="评价", default=daily_evaluate_default)

    def __str__(self):
        return "创建人：" + self.create_by + " 日报时间：" + str(self.date)

    def to_json(self):
        if self.send_status:
            send_describe = "已发送"
        else:
            send_describe = "已保存"
        return {
            "id": self.id,
            "content": self.content,
            "date": str(self.date),
            "create_by": self.create_by,
            "create_name": self.create_name,
            "send_describe": send_describe,
            "template_id": self.template_id,
            "evaluate": self.evaluate,
        }

    def add_evaluate(self, username, content):
        self.evaluate = [evaluate for evaluate in self.evaluate if not evaluate["name"] == username]
        self.evaluate.append({"name": username, "evaluate": content})
        self.save()

    def remove_evaluate(self, username):
        sign = self.evaluate
        self.evaluate = [evaluate for evaluate in self.evaluate if not evaluate["name"] == username]
        self.save()
        if self.evaluate == sign:
            return False
        else:
            return True


# 请假表
class OffDay(TimeBasic):
    start_date = models.DateField(verbose_name="请假开始日期")
    end_date = models.DateField(verbose_name="请假结束日期")
    reason = models.TextField(verbose_name="请假理由")
    user = models.CharField(max_length=128, verbose_name="请假人用户名")

    class Meta:
        unique_together = (
            "start_date",
            "user",
            "end_date",
        )

    def __str__(self):
        return "请假日期：" + str(self.start_date) + str(self.end_date) + " 请假理由：" + self.reason + "请假人用户名" + self.user

    def to_json(self):
        return {
            "id": self.id,
            "start_date": self.start_date.strftime("%Y-%m-%d"),
            "end_date": self.start_date.strftime("%Y-%m-%d"),
            "reason": self.reason,
            "user": self.user,
        }


class Holiday(TimeBasic):
    year = models.IntegerField(verbose_name="年份")
    month = models.IntegerField(verbose_name="月份")
    day = models.IntegerField(verbose_name="日期")
    is_holiday = models.BooleanField(verbose_name="是否为节假日")
    note = models.CharField(max_length=255, verbose_name="备注")

    class Meta:
        unique_together = ("year", "month", "day")

    def __str__(self):
        return "{}-{}-{} {}".format(self.year, self.month, self.day, self.note)
