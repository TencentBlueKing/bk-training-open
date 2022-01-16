import datetime

from django.db import models

from home_application.models import TimeBasic, User

EARLIEST_TIME = datetime.time(8, 0)  # 允许空闲时间的最早时间：08:00
LATEST_TIME = datetime.time(22, 0)  # 允许空闲时间的最晚时间：22:00


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
        name = User.objects.filter(username__in=username_list).values_list("name", flat=True)
        for i in range(0, len(username_list)):
            res.append(
                {
                    "username": username_list[i] + "(" + name[i] + ")",
                    "free_time": [
                        {
                            "id": f_time.id,
                            "date": f_time.start_time.date(),
                            "start_time": f_time.start_time.strftime("%Y-%m-%d %H:%M"),
                            "end_time": f_time.end_time.strftime("%Y-%m-%d %H:%M"),
                        }
                        for f_time in free_times.filter(username=username_list[i])
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
