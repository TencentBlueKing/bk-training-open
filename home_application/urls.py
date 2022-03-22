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

from home_application import views

urlpatterns = (
    path("", views.home),
    path("get_group_info/<int:group_id>/", views.get_group_info),
    url(r"^add_group/$", views.add_group),
    path("delete_group/<int:group_id>/", views.delete_group),
    path("update_group/<int:group_id>/", views.update_group),
    url(r"^get_all_bk_users/$", views.get_all_bk_users),
    path("add_user/<int:group_id>/", views.add_user),
    path("daily_report/", views.daily_report),
    path("report_filter/<int:group_id>/", views.report_filter),
    url(r"^get_user/$", views.get_user),
    url(r"^get_user_groups/$", views.get_user_groups),
    path("get_group_users/<int:group_id>/", views.get_group_users),
    path("exit_group/<int:group_id>/", views.exit_group),
    path("list_admin_group/", views.list_admin_group),
    path("list_member_daily/<int:group_id>/", views.list_member_daily),
    path("list_group_admin/<int:group_id>/", views.list_group_admin),
    path("evaluate_daily/", views.evaluate_daily),  # 评价
    path("notice_non_report_users/<int:group_id>/", views.notice_non_report_users),  # 给未写日报人发送邮件
    url(r"^get_available_apply_groups/$", views.get_available_apply_groups),
    url(r"^apply_for_group/$", views.apply_for_group),
    path("get_apply_for_group_users/<int:group_id>/", views.get_apply_for_group_users),
    path("deal_join_group/<int:group_id>/", views.deal_join_group),
    path("get_reports_dates/", views.get_reports_dates),
    path("delete_evaluate_daily/<int:group_id>/<int:daily_id>/", views.delete_evaluate_daily),
    path("update_evaluate_daily/<int:group_id>/<int:daily_id>/", views.update_evaluate_daily),
    path("send_evaluate_all/<int:group_id>/", views.send_evaluate_all),
    path("add_off_info/", views.add_off_info),
    path("display_personnel_information/<int:group_id>/", views.display_personnel_information),
    path("remove_off/<int:group_id>/<int:offday_id>/", views.remove_off),
    path("check_yesterday_daliy/", views.check_yesterday_daily),
    path("update_daily_perfect_status/<int:group_id>/<int:daily_id>/", views.update_daily_perfect_status),
    path("get_prefect_dailys/<int:group_id>/", views.get_prefect_dailys),
    path("free_time/", views.free_time_get_post),
    path("free_time/<int:free_time_id>/", views.free_time_patch_delete),
    path("group_free_time/<int:group_id>/", views.group_free_time),
    path("check_user_in_group/<int:group_id>/", views.check_user_in_group),
    path("check_user_admin/", views.check_user_admin),
    path("user_free_time/", views.user_free_time),
    # 节假日信息接口
    path("workday_info/", views.get_workday_info),
    path("get_holidays/", views.get_holidays),
)
