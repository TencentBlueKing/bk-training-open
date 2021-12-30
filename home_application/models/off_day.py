from django.db import models

from .common import TimeBasic


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
