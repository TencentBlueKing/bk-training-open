# Generated by Django 2.2.6 on 2021-11-24 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home_application", "0012_auto_20211123_1722"),
    ]

    operations = [
        migrations.CreateModel(
            name="ApplyForGroup",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("create_time", models.DateTimeField(auto_now_add=True, verbose_name="创建时间")),
                ("update_time", models.DateTimeField(auto_now=True, verbose_name="更新时间")),
                ("group_id", models.IntegerField(verbose_name="组id")),
                ("user_id", models.IntegerField(verbose_name="用户id")),
                ("operator", models.IntegerField(verbose_name="处理人id")),
                ("status", models.BooleanField(verbose_name="申请状态")),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.DeleteModel(
            name="ApplyJoinGroup",
        ),
    ]
