from django.db import models

from .common import TimeBasic


# 用户表
class User(TimeBasic):
    username = models.CharField(max_length=128, unique=True, verbose_name="用户账号")
    name = models.CharField(max_length=128, null=True, blank=True, verbose_name="用户姓名")
    phone = models.CharField(max_length=30, null=True, blank=True, verbose_name="电话号码")
    email = models.EmailField(null=True, blank=True, verbose_name="邮箱")

    def __str__(self):
        return self.username
