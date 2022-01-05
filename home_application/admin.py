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

from django.contrib import admin

# 将节假日表注册到管理员页面
from home_application.models import (
    ApplyForGroup,
    Daily,
    FreeTime,
    Group,
    GroupUser,
    Holiday,
    OffDay,
    User,
)

# Register your models here.


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ["year", "month", "day", "is_holiday", "note"]
    list_filter = ["year", "month", "is_holiday"]
    search_fields = ["note"]


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["username", "name", "phone", "email"]
    search_fields = ["username", "name"]


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ["name", "create_by", "create_time", "update_time"]


@admin.register(ApplyForGroup)
class ApplyForGroupAdmin(admin.ModelAdmin):
    list_display = ["group_id", "user_id", "operator", "status"]
    list_filter = ["group_id", "status"]


@admin.register(GroupUser)
class GroupUserAdmin(admin.ModelAdmin):
    list_display = ["group_id", "user_id"]
    list_filter = ["group_id"]


@admin.register(Daily)
class DailyAdmin(admin.ModelAdmin):
    list_display = ["create_by", "create_name", "date", "is_normal", "is_perfect"]
    search_fields = ["create_by", "create_name"]
    list_filter = ["is_normal", "is_perfect"]


@admin.register(FreeTime)
class FreeTimeAdmin(admin.ModelAdmin):
    list_display = ["username", "start_time", "end_time"]
    search_fields = ["username"]


@admin.register(OffDay)
class OffDayAdmin(admin.ModelAdmin):
    list_display = ["user", "start_date", "end_date", "reason"]
    list_filter = ["user"]
