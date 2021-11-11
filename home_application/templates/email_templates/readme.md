# home_application的模板说明

## daily_report.html
!!! 不建议使用，第一次写，技术不够，没有考虑复用，暂时只能拿来发前一天的日报

发送前一天日报模板，需要的参数为：
+ mail_title       邮件标题
+ mail_subhead     邮件副标题
+ group_reports    一个小组的日报内容，为list变量

在group_reports的子项中需要包含
- report_user      日报人姓名，格式统一为username(name)
- report_content   日报内容，json数据，与数据库一致

用法示例在`home_application/celery_task.py.send_yesterday_report()`中

## simple_notify.html

发送简单的通知，需要的参数为：

+ notify_title     通知标题
+ notify_content   通知正文
+ button_text      按钮文字，可选
+ button_link      按钮链接，可选，只有在button_text有效时可用

用法示例
```pycon
html_template = get_template("simple_notify.html")
mail_content = html_template.render(
    {
        "notify_title": "日报提醒",
        "notify_content": "Hi,你今天还写日报，是不是忘记？快来写吧",
        "button_text": "点我去写日报",
        "button_link": "https://paas-edu.bktencent.com/t/train-test/"
    }
)
```