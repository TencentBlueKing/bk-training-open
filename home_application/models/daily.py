from django.db import models
from django_mysql.models import JSONField

from home_application.models import TimeBasic


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

    def add_evaluate(self, username, name, content):
        """
        添加评论，调用时需保证username和nickname为同一个用户
        :param username: 用户名（账号）
        :param name: 用户名（姓名）
        :param content: 评价内容
        :return:
        """
        self.evaluate = [evaluate for evaluate in self.evaluate if not evaluate["username"] == username]
        self.evaluate.append({"username": username, "name": name, "evaluate": content})
        self.save()

    def remove_evaluate(self, username):
        sign = self.evaluate
        self.evaluate = [evaluate for evaluate in self.evaluate if not evaluate["username"] == username]
        self.save()
        if self.evaluate == sign:
            return False
        else:
            return True
