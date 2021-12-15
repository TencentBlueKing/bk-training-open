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
import datetime

from django.db import models
from django_mysql.models import JSONField

EARLIEST_TIME = datetime.time(8, 0)  # 允许空闲时间的最早时间：08:00
LATEST_TIME = datetime.time(22, 0)  # 允许空闲时间的最晚时间：22:00


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
    is_normal = models.BooleanField(verbose_name="是否为当天日报（补签）", default=True)
    is_perfect = models.BooleanField(verbose_name="是否为优秀日报", default=False)

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
            "is_normal": self.is_normal,
            "is_perfect": self.is_perfect,
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


class FreeTimeManage(models.Manager):
    @staticmethod
    def _is_valid_list(free_times: list):
        """
        判断升序排列的多个时间段是否合法
        :param free_times:  升序排列的时间段list，其中每个元素格式为
                                                {
                                                    "start_time":xxx, 	# datetime类型参数，不能是字符串
                                                    "end_time":xxx		# datetime类型参数，不能是字符串
                                                }
        :return:    status, msg     返回两个变量，第一个为bool，说明是否冲突；第二个为str，在冲突时返回具体原因，不冲突的话为"success"
                    True, "success" 或 False, "冲突的具体原因"
        """
        # 判断是否合法：
        # 每个时间段起止时间为同一天且当前时间段的结束早于下个时间段的开始
        free_times_len = len(free_times)
        for index in range(0, free_times_len):
            cur_time = free_times[index]
            # 必须为同一日期
            if cur_time["start_time"].date() != cur_time["end_time"].date():
                return False, "[{}]和[{}]不在同一天".format(
                    cur_time["start_time"].strftime("%Y-%m-%d %H:%M"), cur_time["end_time"].strftime("%Y-%m-%d %H:%M")
                )
            # 起始时间需早于终止时间
            if cur_time["start_time"] >= cur_time["end_time"]:
                return False, "结束时间[{}]需要晚于起始时间[{}]".format(
                    cur_time["start_time"].strftime("%Y-%m-%d %H:%M"), cur_time["end_time"].strftime("%Y-%m-%d %H:%M")
                )
            # 时间范围为8点到22点
            if cur_time["start_time"].time() < EARLIEST_TIME or cur_time["end_time"].time() > LATEST_TIME:
                return False, "[{}]-[{}]空闲时间只能在早上8点（包含）到晚上10点（包含）之间".format(
                    cur_time["start_time"].strftime("%Y-%m-%d %H:%M"),
                    cur_time["end_time"].strftime("%Y-%m-%d %H:%M"),
                )
            if index != free_times_len - 1:
                next_time = free_times[index + 1]
                if cur_time["end_time"] > next_time["start_time"]:
                    return False, "在您已有的空闲时间和要添加的空闲时间中存在交叉：[{}]-[{}]与[{}]-[{}]".format(
                        cur_time["start_time"].strftime("%Y-%m-%d %H:%M"),
                        cur_time["end_time"].strftime("%Y-%m-%d %H:%M"),
                        next_time["start_time"].strftime("%Y-%m-%d %H:%M"),
                        next_time["end_time"].strftime("%Y-%m-%d %H:%M"),
                    )
        return True, "success"

    def is_valid_time(
        self,
        username: str,
        free_times: list,
        old_free_time_id=None,
    ):
        """
        判断要新添加的空闲时间段是否合法
        :param username:            用户名
        :param free_times:          新空闲时间段list，其中每个元素格式为
                                    {
                                        "start_time":xxx, 	# datetime类型参数，不能是字符串
                                        "end_time":xxx		# datetime类型参数，不能是字符串
                                    }
        :param old_free_time_id:    int类型，待修改时间段id，修改空闲时间时需要忽略自身，判断修改后的时间段是否与其他时间段冲突，默认为None，只有在更新是使用
        :return:    status, msg     返回两个变量，第一个为bool，说明是否冲突；第二个为str，在冲突时返回具体原因，不冲突的话为"success"
                    True, "success" 或 False, "冲突的具体原因"
        """
        # 根据开始时间升序排序，然后找出最早和最晚的时间去查询这中间的数据
        free_times = sorted(free_times, key=lambda t: t["start_time"])
        earliest_start_time = free_times[0]["start_time"]
        latest_end_time = free_times[-1]["end_time"]

        # 查询earliest_start_time和latest_end_time之间的时间段，如果是更新某条数据要去掉这条数据本身
        free_time_query_set = self.filter(
            username=username, end_time__gt=earliest_start_time, start_time__lt=latest_end_time
        ).exclude(id=old_free_time_id)

        # 将数据库中的时间段和要添加的时间段合并成总时间段
        all_free_times = [
            {"start_time": f_time.start_time, "end_time": f_time.end_time} for f_time in free_time_query_set
        ]
        all_free_times.extend(free_times)

        all_free_times = sorted(all_free_times, key=lambda t: t["start_time"])
        return self._is_valid_list(all_free_times)

    def add_free_time(self, username: str, free_times: list):
        """
        添加空闲时间段
        :param username:        用户名
        :param free_times:      新空闲时间段list，其中每个元素格式为
                                {
                                    "start_time":xxx, 	# datetime类型参数，不能是字符串
                                    "end_time":xxx		# datetime类型参数，不能是字符串
                                }
        :return:    status, msg     返回两个变量，第一个为bool，说明添加数据是否成功；第二个为str，在添加失败时返回具体原因，成功的话为"success"
                    e.g. True, "success" 或 False, "冲突的具体原因"
        """
        valid_status, valid_msg = self.is_valid_time(username, free_times)
        if not valid_status:
            return valid_status, valid_msg

        # 将free_times转成FreeTime对象，然后批量插入数据库
        free_time_list = []
        for f_time in free_times:
            free_time_list.append(
                self.model(username=username, start_time=f_time["start_time"], end_time=f_time["end_time"])
            )
        self.bulk_create(free_time_list)
        return True, "success"

    @staticmethod
    def get_free_time(username_list: list, start_date: datetime.date, end_date: datetime.date):
        """
        根据用户名list和起止时间查询空闲时间
        :param username_list:   用户名list
        :param start_date:      起始日期（包含）
        :param end_date:        终止日期（包含）
        :return:                用户的空闲时间
        """
        end_date += datetime.timedelta(days=1)
        free_times = FreeTime.objects.filter(
            username__in=username_list, start_time__range=(start_date, end_date)
        ).order_by("start_time")
        res = []
        for username in username_list:
            res.append(
                {
                    "username": username,
                    "free_time": [
                        {
                            "id": f_time.id,
                            "date": f_time.start_time.date(),
                            "start_time": f_time.start_time.strftime("%Y-%m-%d %H:%M"),
                            "end_time": f_time.end_time.strftime("%Y-%m-%d %H:%M"),
                        }
                        for f_time in free_times.filter(username=username)
                    ],
                }
            )
        return res


class FreeTime(TimeBasic):
    # 关于空闲时间的操作
    # 如果没有特殊需求，请使用save的方式更新数据，如需使用update方法，请保证更新后的空闲时间段没有冲突
    start_time = models.DateTimeField(verbose_name="当天有空时间段的起始时间")
    end_time = models.DateTimeField(verbose_name="当天有空时间段的结束时间")
    username = models.CharField(max_length=128, verbose_name="用户名")

    objects = FreeTimeManage()

    def __str__(self):
        return "%s的空闲时间" % self.username

    def save(self, *args, **kwargs):
        """
        :return:    status, msg     返回两个变量，第一个为bool，说明是否冲突；第二个为str，在冲突时返回具体原因，不冲突的话为"success"
                    True, "success" 或 False, "冲突的具体原因"
        """
        cur_free_time = [{"start_time": self.start_time, "end_time": self.end_time}]
        valid_status, valid_msg = FreeTime.objects.is_valid_time(self.username, cur_free_time, self.id)
        if not valid_status:
            return valid_status, valid_msg
        else:
            super().save()
            return True, "success"
