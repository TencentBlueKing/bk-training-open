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

from django.db import models


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
    # 多个管理员用户名拼接成的字符串
    admin = models.CharField(max_length=255, verbose_name="管理员们")
    create_by = models.CharField(max_length=128, verbose_name="创建人")

    def __str__(self):
        return self.name

    def admin_include(self, username: str) -> bool:
        """
        判断管理员列表是否包含指定用户
        :param username: 用户名
        :return: 是→True；不是→False
        """
        return username in self.admin


# 组中的日报通知人
class GroupNotifier(models.Model):
    group_id = models.IntegerField(verbose_name="组id")
    daily_notifier_id = models.IntegerField(verbose_name="日报通知人")

    def __str__(self):
        return "组id是：" + str(self.group_id) + " 日报通知人id：" + str(self.daily_notifier_id)


class GenderType:
    MALE = 0
    FEMALE = 1


# 用户表
class User(TimeBasic):
    username = models.CharField(max_length=128, unique=True, verbose_name="用户账号")
    name = models.CharField(max_length=128, verbose_name="用户姓名")
    gender = models.IntegerField(
        choices=[(GenderType.MALE, "男"), (GenderType.FEMALE, "女")], null=True, blank=True, verbose_name="性别"
    )
    phone = models.IntegerField(null=True, blank=True, verbose_name="电话号码")
    email = models.EmailField(verbose_name="邮箱")

    def __str__(self):
        return self.username


# 组-用户关联表
class GroupUser(models.Model):
    group_id = models.IntegerField(verbose_name="组id")
    user_id = models.IntegerField(verbose_name="用户id")

    def __str__(self):
        return "组id：" + str(self.group_id) + " 用户id：" + str(self.user_id)


# 组-模板关联表
class TemplateGroup(models.Model):
    group_id = models.IntegerField(verbose_name="组id")
    template_id = models.IntegerField(verbose_name="模板id")

    def __str__(self):
        return "组id：" + str(self.group_id) + " 日报模板id：" + str(self.template_id)


# 日报模板表
class DailyReportTemplate(models.Model):
    # 改成128
    name = models.CharField(max_length=128, verbose_name="日报模板名字")
    content = models.CharField(max_length=255, verbose_name="日报模板内容")
    create_by = models.CharField(max_length=128, verbose_name="创建人")

    def __str__(self):
        return self.name


# 日报表
class Daily(TimeBasic):
    content = models.TextField(verbose_name="日报内容")
    create_by = models.CharField(max_length=128, verbose_name="创建人")
    date = models.DateTimeField(verbose_name="日报日期")

    def __str__(self):
        return "创建人：" + self.create_by + " 日报时间：" + str(self.date)
