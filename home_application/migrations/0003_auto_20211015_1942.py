# Generated by Django 2.2.6 on 2021-10-15 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home_application", "0002_auto_20211012_1721"),
    ]

    operations = [
        migrations.DeleteModel(
            name="TemplateGroup",
        ),
        migrations.AddField(
            model_name="dailyreporttemplate",
            name="group_id",
            field=models.IntegerField(default=1, verbose_name="组id"),
            preserve_default=False,
        ),
    ]