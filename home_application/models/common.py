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

    def to_json(self):
        return {"date": f"{self.year}-{self.month}-{self.day}", "is_holiday": self.is_holiday, "note": self.note}


# 用户表
class User(TimeBasic):
    username = models.CharField(max_length=128, unique=True, verbose_name="用户账号")
    name = models.CharField(max_length=128, null=True, blank=True, verbose_name="用户姓名")
    phone = models.CharField(max_length=30, null=True, blank=True, verbose_name="电话号码")
    email = models.EmailField(null=True, blank=True, verbose_name="邮箱")

    def __str__(self):
        return self.username
