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

from home_application.views import common, daily, free_time, group, off_day, user

urlpatterns = (
    path("", common.home),
    path("report_template/<int:group_id>/", daily.report_template),
    path("get_all_report_template/", daily.get_all_report_template),
    path("get_group_info/<int:group_id>/", group.get_group_info),
    url(r"^add_group/$", group.add_group),
    path("delete_group/<int:group_id>/", group.delete_group),
    path("update_group/<int:group_id>/", group.update_group),
    url(r"^get_all_bk_users/$", common.get_all_bk_users),
    path("add_user/<int:group_id>/", user.add_user),
    path("daily_report/", daily.daily_report),
    path("report_filter/<int:group_id>/", user.report_filter),
    url(r"^update_user/$", user.update_user),
    url(r"^get_user/$", user.get_user),
    url(r"^get_user_groups/$", group.get_user_groups),
    path("get_group_users/<int:group_id>/", group.get_group_users),
    path("exit_group/<int:group_id>/", group.exit_group),
    path("list_admin_group/", group.list_admin_group),
    path("list_member_daily/<int:group_id>/", daily.list_member_daily),
    path("list_group_admin/<int:group_id>/", group.list_group_admin),
    path("evaluate_daily/", daily.evaluate_daily),  # 评价
    path("notice_non_report_users/<int:group_id>/", daily.notice_non_report_users),  # 给未写日报人发送邮件
    url(r"^get_available_apply_groups/$", group.get_available_apply_groups),
    url(r"^apply_for_group/$", group.apply_for_group),
    path("get_apply_for_group_users/<int:group_id>/", group.get_apply_for_group_users),
    path("deal_join_group/<int:group_id>/", group.deal_join_group),
    path("get_reports_dates/", daily.get_reports_dates),
    path("delete_evaluate_daily/<int:group_id>/<int:daily_id>/", daily.delete_evaluate_daily),
    path("update_evaluate_daily/<int:group_id>/<int:daily_id>/", daily.update_evaluate_daily),
    path("send_evaluate_all/<int:group_id>/", daily.send_evaluate_all),
    path("add_off_info/", off_day.add_off_info),
    path("display_personnel_information/<int:group_id>/", off_day.display_personnel_information),
    path("remove_off/<int:group_id>/<int:offday_id>/", off_day.remove_off),
    path("check_yesterday_daliy/", daily.check_yesterday_daily),
    path("update_daily_perfect_status/<int:group_id>/<int:daily_id>/", daily.update_daily_perfect_status),
    path("get_prefect_dailys/<int:group_id>/", daily.get_prefect_dailys),
    path("free_time/", free_time.free_time_get_post),
    path("free_time/<int:free_time_id>", free_time.free_time_patch_delete),
    path("group_free_time/<int:group_id>", free_time.group_free_time),
    path("check_user_in_group/<int:group_id>/", group.check_user_in_group),
    path("check_user_admin/", user.check_user_admin),
)
