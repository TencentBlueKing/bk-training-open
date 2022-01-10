import json
from datetime import timedelta

from django.http import JsonResponse
from django.utils.datetime_safe import datetime
from django.views.decorators.http import require_GET, require_http_methods

from home_application.celery_task import send_evaluate_daily, send_good_daily
from home_application.models import Daily, Group, GroupUser, OffDay, User
from home_application.utils.calendar_util import CalendarHandler
from home_application.utils.decorator import is_group_member
from home_application.utils.mail_operation import remind_to_write_daily
from home_application.utils.report_operation import content_format_as_json
from home_application.utils.tools import check_user_is_admin, get_paginator

# 开发框架中通过中间件默认是需要登录态的，如有不需要登录的，可添加装饰器login_exempt
# 装饰器引入 from blueapps.account.decorators import login_exempt


@require_http_methods(["POST", "GET"])
def daily_report(request):
    """日报模块的增删改查"""
    # 获取今天的日报，没有就返回空-------------------------------------------------------------------------------
    if request.method == "GET":
        # 获取日期
        date = request.GET.get("date")
        try:
            date = datetime.strptime(date, "%Y-%m-%d").date()
            today_report = Daily.objects.get(create_by=request.user.username, date=date)
            return JsonResponse({"result": True, "code": 0, "message": "获取日报成功", "data": today_report.to_json()})
        except ValueError:
            return JsonResponse({"result": False, "code": -1, "message": "日期格式错误", "data": []})
        except Daily.DoesNotExist:
            return JsonResponse({"result": True, "code": 0, "message": "这一天还没有写日报", "data": {}})

    # 参数校验-----------------------------------------------------------------------------------------
    req = json.loads(request.body)
    report_content = req.get("content")
    report_date_str = req.get("date")
    try:
        report_date = datetime.strptime(report_date_str, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({"result": False, "code": -1, "message": "日期格式错误", "data": []})
    if report_date > datetime.today():
        return JsonResponse({"result": False, "code": -1, "message": "日期不合法", "data": []})

    # 添加或修改日报--------------------------------------------------------------------------------------
    if request.method == "POST":
        try:
            # 修改日报
            target_report = Daily.objects.get(create_by=request.user.username, date=report_date)
            # 日报如果已经发送管理员审核的话就直接返回不可修改
            if target_report.send_status:
                return JsonResponse({"result": False, "code": -1, "message": "日报已经发送管理员查看，不可修改", "data": []})
            target_report.content = report_content
            target_report.save()
            message = "修改日报成功"
        except Daily.DoesNotExist:
            # 抛出异常表示找不到，说明还没有写日报，可以添加新的日报
            create_name = request.user.nickname

            # 如果是补签之前的日报直接修改发送状态为'已发送'，但是在当天10点之前补签昨天的日报仍为'未发送'
            datetime_now = datetime.now()
            if datetime_now.hour < 10:
                # 填写日期在10点前，日报日期在昨天(今天-1天)之前就是补签
                send_status = report_date < (datetime_now - timedelta(days=1)).date()
            else:
                # 填写日期在10点后，日报日期小于当天就是补签
                send_status = report_date < datetime_now.date()

            Daily.objects.create(
                content=report_content,
                create_by=request.user.username,
                create_name=create_name,
                date=report_date,
                # TODO 移除日报模板相关内容
                template_id=0,
                send_status=send_status,
                is_normal=not send_status,
            )
            if send_status:
                message = "补写日报成功"
            else:
                message = "保存日报成功"
        return JsonResponse({"result": True, "code": 0, "message": message, "data": []})


@require_GET
def get_reports_dates(request):
    """获取用户已提交的所有日报日期"""
    member_dates = Daily.objects.filter(create_by=request.user.username, send_status=True).values_list(
        "date", flat=True
    )
    return JsonResponse({"result": True, "code": 0, "message": "获取日报成功", "data": list(member_dates)})


@require_GET
def check_yesterday_daily(request):
    """检查工作日日报是否已填写"""
    yesterday = datetime.now() - timedelta(days=1)
    if check_user_is_admin(request, 0):
        return JsonResponse({"result": True, "code": 0, "message": "管理员不需写日报", "data": True})
    if CalendarHandler(yesterday).is_holiday:
        return JsonResponse({"result": True, "code": 0, "message": "昨天非工作日", "data": []})
    try:
        Daily.objects.get(create_by=request.user.username, date=yesterday)
    except Daily.DoesNotExist:
        return JsonResponse({"result": False, "code": 0, "message": "昨天没有写日报", "data": []})
    return JsonResponse({"result": True, "code": 0, "message": "昨天已写日报", "data": []})


@is_group_member(admin_needed=["PATCH"])
def update_daily_perfect_status(request, group_id, daily_id):
    """修改日报的优秀状态"""
    try:
        daily = Daily.objects.get(id=daily_id)
        Daily.objects.filter(id=daily_id).update(is_perfect=not daily.is_perfect)
    except Daily.DoesNotExist:
        return JsonResponse({"result": False, "code": 1, "message": "日报不存在", "data": []})
    return JsonResponse({"result": True, "code": 0, "message": "修改日报是否优秀状态成功", "data": []})


@require_GET
@is_group_member()
def get_prefect_dailys(request, group_id):
    """获取组内优秀日报"""
    # 根据组查询组所有成员用户名
    member_ids = GroupUser.objects.filter(group_id=group_id).values_list("user_id", flat=True)
    member_usernames = User.objects.filter(id__in=member_ids).values_list("username", flat=True)
    select_type = request.GET.get("select_type")
    # 排除管理员
    admin_list = Group.objects.get(id=group_id).admin_list
    member_usernames = set(member_usernames) - set(admin_list)
    # 查询所有优秀日报
    daily_list = Daily.objects.filter(create_by__in=member_usernames, is_perfect=True).order_by("-date")
    if select_type == "month":
        # 查询某月优秀日报
        year = request.GET.get("year")
        month = request.GET.get("month")
        daily_list = daily_list.filter(date__year=year, date__month=month)
    # 日报数量
    total_num = daily_list.count()
    # 分页
    page = request.GET.get("page")
    size = request.GET.get("size")
    daily_list = get_paginator(daily_list, page=page, size=size)
    if daily_list is None:
        return JsonResponse({"result": False, "code": 404, "message": "分页参数异常", "data": []})
    # 返回日报数据
    res_data = {
        "total_num": total_num,
        "daily_list": content_format_as_json(daily_list),
    }
    return JsonResponse({"result": True, "code": 0, "message": "获取优秀日报成功", "data": res_data})


@require_http_methods(["POST"])
def evaluate_daily(request):
    """
    评价组员日报
    """
    req = json.loads(request.body)
    daily_id = req.get("daily_id")
    evaluate_content = req.get("evaluate")
    try:
        evaluate = Daily.objects.get(id=daily_id).evaluate
    except Daily.DoesNotExist:
        return JsonResponse({"result": False, "code": 1, "message": "日报不存在"})
    evaluate.append({"name": request.user.username, "evaluate": evaluate_content})
    Daily.objects.filter(id=daily_id).update(evaluate=evaluate)
    # 获取发邮件人的姓名
    evaluate_user = User.objects.get(username=request.user.username)
    evaluate_name = evaluate_user.username + "(" + evaluate_user.name + ")"
    send_evaluate_daily.apply_async(
        kwargs={"evaluate_name": evaluate_name, "daily_id": daily_id, "evaluate_content": evaluate_content}
    )
    return JsonResponse({"result": True, "code": 0, "message": "点评成功", "data": []})


@require_http_methods(["POST"])
@is_group_member(admin_needed=["POST"])
def notice_non_report_users(request, group_id):
    """
    提醒未写日报成员写日报
    """
    date = json.loads(request.body).get("date")
    # 组内成员
    group_user_ids = GroupUser.objects.filter(group_id=group_id).values_list("user_id", flat=True)
    group_users = User.objects.filter(id__in=group_user_ids).values_list("username", flat=True)
    # 填写日报信息
    report_user_usernames = Daily.objects.filter(create_by__in=group_users, date=date).values_list(
        "create_by", flat=True
    )
    # 管理员不用写日报
    admin_list = Group.objects.get(id=group_id).admin_list
    non_report_users = set(group_users) - set(report_user_usernames) - set(admin_list)
    # 请假的人不用写日报
    off_day_list = OffDay.objects.filter(start_date__lte=date, end_date__gte=date, user__in=non_report_users)
    non_report_users = set(non_report_users) - set(off_day_list)
    # 发送邮件
    if non_report_users:
        remind_to_write_daily.apply_async(kwargs={"username_list": list(non_report_users), "date": date})
        return JsonResponse({"result": True, "code": 0, "message": "一键提醒成功", "data": []})
    else:
        return JsonResponse({"result": True, "code": 0, "message": "无未写日报成员", "data": []})


@require_http_methods(["DELETE"])
@is_group_member(admin_needed=["DELETE"])
def delete_evaluate_daily(request, group_id, daily_id):
    """
    删除日报中评价
    仅可以删除自己的
    """
    username = request.user.username
    daily = Daily.objects.get(id=daily_id)
    if daily.remove_evaluate(username):
        return JsonResponse({"result": True, "code": 0, "message": "删除成功", "data": []})
    else:
        return JsonResponse({"result": False, "code": 0, "message": "评价不存在", "data": []})


@require_http_methods(["POST"])
@is_group_member(admin_needed=["POST"])
def update_evaluate_daily(request, group_id, daily_id):
    """
    修改日报的指定评论
    """
    try:
        daily = Daily.objects.get(id=daily_id)
    except Daily.DoesNotExist:
        return JsonResponse({"result": False, "code": 0, "message": "无此日报", "data": []})
    evaluate_content = json.loads(request.body).get("evaluate_content")
    username = request.user.username
    daily.add_evaluate(username, evaluate_content)
    return JsonResponse({"result": True, "code": 0, "message": "修改成功", "data": []})


@require_http_methods(["POST"])
@is_group_member(admin_needed=["POST"])
def send_evaluate_all(request, group_id):
    """
    发生邮件给所有组成员
    可以发生多个邮件
    """
    daily_ids = json.loads(request.body).get("daily_ids")
    date = Daily.objects.get(id=daily_ids[0]).date
    # 标记 是否找到该管理员的评价
    sign = True
    # 日报信息列表
    daily_list = []
    dailys = Daily.objects.filter(id__in=daily_ids)
    for daily in dailys:
        daily = daily.to_json()
        daily["create_name"] = daily["create_by"] + "(" + daily["create_name"] + ")"
        for evaluate in daily["evaluate"]:
            if evaluate["name"] == request.user.username:
                daily["evaluate"] = evaluate["evaluate"]
                sign = False
                break
        if sign:
            daily["evaluate"] = "管理员未评价"
        daily_list.append(daily)
        sign = True
    #  组内所有人
    user_id = GroupUser.objects.filter(group_id=group_id).values_list("user_id", flat=True)
    all_username_list = User.objects.filter(id__in=user_id).values_list("username", flat=True)
    # 排除管理员
    admin_list = Group.objects.get(id=group_id).admin_list
    all_username_list = set(all_username_list) - set(admin_list)
    evaluate_user = User.objects.get(username=request.user.username)
    if all_username_list:
        # 放进celery里
        all_username_list = ",".join(all_username_list)
        send_good_daily.apply_async(
            kwargs={
                "evaluate_name": evaluate_user.username + "(" + evaluate_user.name + ")",
                "all_username_list": all_username_list,
                "date": date,
                "daily_list": daily_list,
            }
        )
        return JsonResponse({"result": True, "code": 0, "message": "发送成功", "data": []})
    else:
        return JsonResponse({"result": False, "code": 0, "message": "这个组没有成员", "data": []})


@require_http_methods(["GET"])
@is_group_member(admin_needed=["GET"])
def list_member_daily(request, group_id):
    """
    获取成员的日报信息
    """
    today = datetime.today().date()
    date = request.GET.get("date", today)
    # 组内成员
    group_members = GroupUser.objects.filter(group_id=group_id)
    users = User.objects.filter(id__in=group_members.values_list("user_id", flat=True))
    # 日报信息
    dailies = Daily.objects.filter(date=date, create_by__in=users.values_list("username", flat=True))
    # 拼接响应
    data = []
    for user in users:
        try:
            daily = dailies.get(create_by=user.username).to_json()
            daily["write_status"] = True
        except Daily.DoesNotExist:
            daily = Daily(date=date, create_by=user.username, create_name=user.name, content=[]).to_json()
            daily["write_status"] = False
        data.append(daily)
    return JsonResponse({"result": True, "code": 0, "message": "", "data": data})


@require_GET
@is_group_member()
def report_filter(request, group_id):
    # 根据成员id分页获取他最近的日报-----------------------------------------------------------------------------
    member_id = request.GET.get("member_id")
    page = request.GET.get("page")
    # 每一页显示日报数量
    page_size = request.GET.get("size", 8)
    if member_id:
        # 根据member_id参数判断是根据成员id还是日期获取日报，
        try:
            # 安全校验，查看目标对象是否为同组成员
            GroupUser.objects.get(group_id=group_id, user_id=member_id)
            member_name = User.objects.get(id=member_id).username
        except GroupUser.DoesNotExist:
            return JsonResponse({"result": False, "code": -1, "message": "与目标用户非同组成员，查询被拒绝", "data": []})
        except User.DoesNotExist:
            return JsonResponse({"result": False, "code": -1, "message": "目标用户不存在", "data": []})
        except ValueError:
            return JsonResponse({"result": False, "code": -1, "message": "日报数量无效", "data": []})

        # 查询当前成员的日报，按照日期降序
        member_report = Daily.objects.filter(create_by=member_name).order_by("-date")
        total_report_num = member_report.count()

        # 分页
        member_report = get_paginator(member_report, page, page_size)
        if member_report is None:
            return JsonResponse({"result": False, "code": 404, "message": "分页参数异常", "data": []})
        # 查询完毕返回数据
        res_data = {"total_report_num": total_report_num, "reports": content_format_as_json(member_report)}
        return JsonResponse({"result": True, "code": 0, "message": "查询日报成功", "data": res_data})

    # 根据日期获取组内所有成员的日报------------------------------------------------------------------------------
    report_date = request.GET.get("date")
    try:
        report_date = datetime.strptime(report_date, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({"result": False, "code": -1, "message": "日期格式错误", "data": []})
    # 查询组内所有人
    # 首选获取组内成员的id，然后再去查询成员对应的username
    member_in_group = GroupUser.objects.filter(group_id=group_id).values_list("user_id", flat=True)
    member_in_group = User.objects.filter(id__in=member_in_group).values_list("username", flat=True)
    # 查询所有人的日报
    member_report = Daily.objects.filter(date=report_date, create_by__in=member_in_group).order_by("-date")
    total_report_num = member_report.count()
    # 查找自己的日报
    get_my_report = True
    if not CalendarHandler(report_date).is_holiday:
        try:
            Daily.objects.get(date=report_date, create_by=request.user.username)
        except Daily.DoesNotExist:
            get_my_report = False
    if check_user_is_admin(request, 0):
        get_my_report = True
    # 分页
    member_report = get_paginator(member_report, page, page_size)
    if member_report is None:
        return JsonResponse({"result": False, "code": 404, "message": "分页参数异常", "data": []})
    # 查询完毕返回数据
    res_data = {
        "total_report_num": total_report_num,
        "reports": content_format_as_json(member_report),
        "my_today_report": get_my_report,
    }
    return JsonResponse({"result": True, "code": 0, "message": "获取日报成功", "data": res_data})
