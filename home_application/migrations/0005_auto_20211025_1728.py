# Generated by Django 2.2.6 on 2021-10-25 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home_application", "0004_auto_20211018_1709"),
    ]

    operations = [
        migrations.AlterField(
            model_name="daily",
            name="date",
            field=models.DateField(verbose_name="日报日期"),
        ),
    ]
