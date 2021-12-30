from django.db import models


# Create your models here.
# 创建时间和更新时间基类
class TimeBasic(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        abstract = True


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


# 组-用户关联表
class GroupUser(models.Model):
    group_id = models.IntegerField(verbose_name="组id")
    user_id = models.IntegerField(verbose_name="用户id")

    def __str__(self):
        return "组id：" + str(self.group_id) + " 用户id：" + str(self.user_id)

    class Meta:
        unique_together = ("group_id", "user_id")
