# Generated by Django 2.2.6 on 2021-10-18 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home_application', '0003_auto_20211015_1942'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='gender',
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='邮箱'),
        ),
        migrations.AlterField(
            model_name='user',
            name='name',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='用户姓名'),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='电话号码'),
        ),
        migrations.AlterUniqueTogether(
            name='groupnotifier',
            unique_together={('group_id', 'daily_notifier_id')},
        ),
        migrations.AlterUniqueTogether(
            name='groupuser',
            unique_together={('group_id', 'user_id')},
        ),
    ]
