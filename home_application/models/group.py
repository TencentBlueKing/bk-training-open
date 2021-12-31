from django.db import models

from home_application.models import TimeBasic


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


# 申请入组表
class ApplyForGroup(TimeBasic):
    group_id = models.IntegerField(verbose_name="组id")
    user_id = models.IntegerField(verbose_name="用户id")
    operator = models.IntegerField(null=True, verbose_name="处理人id")
    status = models.SmallIntegerField(verbose_name="申请状态")

    def __str__(self):
        return "组id：" + str(self.group_id) + " 用户id：" + str(self.user_id)


# 组-用户关联表
class GroupUser(models.Model):
    group_id = models.IntegerField(verbose_name="组id")
    user_id = models.IntegerField(verbose_name="用户id")

    def __str__(self):
        return "组id：" + str(self.group_id) + " 用户id：" + str(self.user_id)

    class Meta:
        unique_together = ("group_id", "user_id")
