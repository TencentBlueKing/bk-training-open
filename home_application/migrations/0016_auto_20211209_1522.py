# Generated by Django 2.2.6 on 2021-12-09 15:22

import django_mysql.models
from django.db import migrations, models

import home_application.models


class Migration(migrations.Migration):

    dependencies = [
        ("home_application", "0015_offday"),
    ]

    operations = [
        migrations.AddField(
            model_name="daily",
            name="is_normal",
            field=models.BooleanField(default=True, verbose_name="是否为当天日报（补签）"),
        ),
        migrations.AddField(
            model_name="daily",
            name="is_perfect",
            field=models.BooleanField(default=False, verbose_name="是否为优秀日报"),
        ),
        migrations.AlterField(
            model_name="daily",
            name="content",
            field=django_mysql.models.JSONField(
                default=home_application.models.daily_content_default, verbose_name="日报内容"
            ),
        ),
    ]
