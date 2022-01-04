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
from home_application.models import Group, Holiday

# Register your models here.


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ["year", "month", "day", "is_holiday", "note"]
    list_filter = ["year", "month", "is_holiday", "note"]
    search_fields = ["note"]
    list_per_page = 15


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ["name", "create_by", "create_time", "update_time"]
