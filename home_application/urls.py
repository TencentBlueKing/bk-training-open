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

from django.conf.urls import url
from django.urls import path

from . import views

urlpatterns = (
    path("report_template/<int:group_id>/", views.report_template),
    url(r"^add_group/$", views.add_group),
    url(r"^update_group/$", views.update_group),
    url(r"^get_all_bk_users/$", views.get_all_bk_users),
    path("add_user/<int:group_id>/", views.add_user),
    url(r"^update_user/$", views.update_user),
    url(r"^get_user/$", views.get_user),
    url(r"^get_user_groups/$", views.get_user_groups),
    path("get_group_users/<int:group_id>/", views.get_group_users),
    url(r"^exit_group/$", views.exit_group),
)
