# Generated by Django 2.2.6 on 2021-11-25 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home_application", "0014_auto_20211124_2149"),
    ]

    operations = [
        migrations.AlterField(
            model_name="applyforgroup",
            name="status",
            field=models.IntegerField(max_length=2, verbose_name="申请状态"),
        ),
    ]
