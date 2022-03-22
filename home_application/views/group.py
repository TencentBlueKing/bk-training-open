import json

from django.db import IntegrityError
from django.http import JsonResponse

# 开发框架中通过中间件默认是需要登录态的，如有不需要登录的，可添加装饰器login_exempt
# 装饰器引入 from blueapps.account.decorators import login_exempt
from django.views.decorators.http import require_http_methods, require_POST

from blueking.component.shortcuts import get_client_by_request
from home_application.celery_task import (
    send_apply_for_group_result,
    send_apply_for_group_to_manager,
)
from home_application.models import ApplyForGroup, Group, GroupUser, User
from home_application.utils.decorator import is_group_member
from home_application.utils.tools import (
    apply_info_to_json,
    apply_is_available_to_json,
    check_param,
)
from home_application.views.user import auto_sign_users


@is_group_member()
def get_group_info(request, group_id):
    group = Group.objects.get(id=group_id)
    admin_usernames = group.admin_list
    admin_list = User.objects.filter(username__in=admin_usernames).values("id", "username", "name")
    data = {
        "id": group.id,
        "name": group.name,
        "admin": group.admin,
        "admin_list": list(admin_list),
        "create_by": group.create_by,
        "create_name": group.create_name,
        "create_time": group.create_time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    return JsonResponse({"result": True, "code": 0, "message": "获取组信息成功", "data": data})


def add_group(request):
    """添加组"""
    req = json.loads(request.body)
    params = {"name": "组名", "admin": "管理员"}
    check_result, message = check_param(params, req)
    if not check_result:
        return JsonResponse({"result": False, "code": 1, "message": message})

    name = req.get("name")
    admins = req.get("admin")
    create_by = request.user.username
    create_name = request.user.nickname

    # 要授权的管理员list
    admin_names = [admin.get("username") for admin in admins]
    if create_by not in admin_names:
        admin_names.insert(0, create_by)

    try:
        group = Group.objects.create(
            name=name, admin=",".join(admin_names), create_by=request.user.username, create_name=create_name
        )
    except IntegrityError:
        return JsonResponse({"result": False, "code": 1, "message": "添加失败，组名重复"})
    # 添加未注册的用户信息
    auto_sign_users(admin_names, admins)
    # 添加组-用户信息
    group_user_list = []
    for admin in admins:
        group_user_list.append(GroupUser(group_id=group.id, user_id=admin.get("id")))
    GroupUser.objects.bulk_create(group_user_list)
    return JsonResponse({"result": True, "code": 0, "message": "success", "data": {"group_id": group.id}})


@is_group_member(admin_needed=["POST"])
def delete_group(request, group_id):
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return JsonResponse({"result": False, "code": -1, "message": "组不存在", "data": []})
    if group.create_by != request.user.username:
        return JsonResponse({"result": False, "code": 1, "message": "无权限", "data": []})
    group.delete()
    GroupUser.objects.filter(group_id=group_id).delete()
    return JsonResponse({"result": True, "code": 0, "message": "删除组成功", "data": []})


@is_group_member(admin_needed=["POST", "PUT", "DELETE"])
def update_group(request, group_id):
    """编辑组信息"""
    req = json.loads(request.body)
    params = {"name": "组名", "admin": "管理员"}
    check_result, message = check_param(params, req)
    if not check_result:
        return JsonResponse({"result": False, "code": 1, "message": message})
    name = req.get("name")
    admins = req.get("admin")

    admin_names = []
    admin_ids = []
    for admin in admins:
        admin_ids.append(admin.get("id"))
        admin_names.append(admin.get("username"))

    if request.user.username not in admin_names:
        return JsonResponse({"result": False, "code": 1, "message": "不允许移除自己", "data": []})

    # 更新管理员，并保持数据库与权限中心一致
    group = Group.objects.get(id=group_id)
    group.admin = ",".join(admin_names)
    group.name = name

    # 添加未注册的用户信息
    auto_sign_users(admin_names, admins)

    # 批量添加用户-组信息
    exist_user_ids = GroupUser.objects.filter(group_id=group_id, user_id__in=admin_ids).values_list(
        "user_id", flat=True
    )
    group_user_list = []
    for admin_id in admin_ids:
        if admin_id not in exist_user_ids:
            group_user_list.append(GroupUser(group_id=group_id, user_id=admin_id))
    GroupUser.objects.bulk_create(group_user_list)

    try:
        group.save()
    except IntegrityError:
        return JsonResponse({"result": False, "code": 1, "message": "更新失败，组名重复", "data": []})
    else:
        return JsonResponse({"result": True, "code": 0, "message": "更新成功", "data": []})


def get_available_apply_groups(request):
    """获取所有(未在、未申请)组信息"""
    # 获取用户已经在的组
    sql_str = (
        "select g.id, g.name, if (gu.id is null, if(apply.id is null, true, false), false) is_available "
        "from home_application_group g "
        "left join home_application_groupuser gu "
        "on g.id = gu.group_id and gu.user_id = %s "
        "left join home_application_applyforgroup apply "
        "on g.id = apply.group_id and apply.user_id = %s and apply.status = 0"
    )
    group_infos = Group.objects.raw(sql_str, [request.user.id, request.user.id])
    group_list = [apply_is_available_to_json(group) for group in group_infos]
    return JsonResponse({"result": True, "code": 0, "message": "获取成功", "data": group_list})


def apply_for_group(request):
    """用户申请入组"""
    req = json.loads(request.body)
    params = {"group_id": "组id"}
    check_result, message = check_param(params, req)
    if not check_result:
        return JsonResponse({"result": False, "code": 1, "message": message})
    group_id = req.get("group_id")
    user_id = request.user.id
    # 获取组信息
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return JsonResponse({"result": False, "code": 0, "message": "组不存在", "data": []})
    # 检查是否已在组中
    try:
        GroupUser.objects.get(group_id=group_id, user_id=user_id)
        # 用户已在组中
        return JsonResponse({"result": False, "code": 1, "message": "用户已在组-{}中".format(group.name), "data": []})
    except GroupUser.DoesNotExist:
        # 用户不在组中
        try:
            ApplyForGroup.objects.get(group_id=group_id, user_id=user_id, status=0)
            # 用户已申请过入组
            return JsonResponse({"result": False, "code": 1, "message": "已申请过入组-{}".format(group.name), "data": []})
        except ApplyForGroup.DoesNotExist:
            # 用户未申请入组
            ApplyForGroup.objects.create(group_id=group_id, user_id=user_id, status=0)
            # 给管理员发送邮件
            # 获取用户信息
            user = User.objects.get(id=user_id)
            send_apply_for_group_to_manager.apply_async(
                kwargs={
                    "group_name": group.name,
                    "group_admins": group.admin,
                    "user_name": "{}({})".format(user.username, user.name),
                    "group_id": group_id,
                }
            )
            return JsonResponse({"result": True, "code": 0, "message": "申请入组-{}成功".format(group.name), "data": []})


@is_group_member(admin_needed=["GET"])
def get_apply_for_group_users(request, group_id):
    """ "获取申请入组列表"""
    # 获取所有申请人id和申请时间
    sql_str = (
        "select user.id, user.username, user.name,apply.update_time "
        "from home_application_applyforgroup apply, home_application_user user "
        "where apply.user_id = user.id and apply.status = 0 and apply.group_id = %s"
    )
    apply_infos = ApplyForGroup.objects.raw(sql_str, [group_id])
    apply_info_list = [apply_info_to_json(info) for info in apply_infos]
    return JsonResponse({"result": True, "code": 0, "message": "获取申请人列表成功", "data": apply_info_list})


@require_POST
@is_group_member(admin_needed=["POST"])
def deal_join_group(request, group_id):
    """管理员同意用户入组"""
    # 校验参数
    req = json.loads(request.body)
    params = {"user_id": "用户id", "status": "处理操作"}
    check_result, message = check_param(params, req)
    if not check_result:
        return JsonResponse({"result": False, "code": 1, "message": message, "data": []})
    user_id = req.get("user_id")

    # 操作 status = 1(同意), status = 2(拒绝)
    status = req.get("status")
    if status == 1:
        status_message = "同意"
    elif status == 2:
        status_message = "拒绝"
    else:
        return JsonResponse({"result": False, "code": 1, "message": "不合法的处理意见", "data": []})

    try:
        user_apply = ApplyForGroup.objects.get(user_id=user_id, group_id=group_id, status=0)

        # 获取用户信息
        user = User.objects.get(id=user_id)
        user_name = "{}({})".format(user.username, user.name)
        # 组名
        group_name = Group.objects.get(id=group_id).name
        # 如果允许入组，添加组-用户信息（入组）
        if status == 1:
            GroupUser.objects.create(group_id=group_id, user_id=user_id)
    except ApplyForGroup.DoesNotExist:
        return JsonResponse({"result": False, "code": 1, "message": "未找到该申请或已经被其他管理员处理", "data": []})
    except IntegrityError:
        return JsonResponse({"result": False, "code": 1, "message": "用户已加入[{}]".format(group_name), "data": []})

    # 发送申请结果给用户
    send_apply_for_group_result.apply_async(
        kwargs={"username": user.username, "group_name": group_name, "status": status}
    )

    # 更新用户的申请信息
    user_apply.status = status
    user_apply.operator = request.user.id
    user_apply.save()

    return JsonResponse(
        {
            "result": True,
            "code": 0,
            "message": f"已{status_message}{user_name}加入[{group_name}]",
            "data": [],
        }
    )


def get_user_groups(request):
    """查询用户组列表"""
    user_id = request.user.id
    group_ids = GroupUser.objects.filter(user_id=user_id).values_list("group_id", flat=True)
    groups = Group.objects.in_bulk(list(group_ids))
    group_list = []
    for group in groups.values():
        admin = group.admin_list
        group_list.append(
            {
                "id": group.id,
                "name": group.name,
                "admin": admin,
                "create_by": group.create_by,
                "create_name": group.create_name,
                "create_time": group.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
    return JsonResponse({"result": True, "code": 0, "message": "查询成功", "data": group_list})


def get_group_users(request, group_id):
    """
    查询组的成员列表
    param sign :标记0 返回不包括管理员的组成员 标记 null 返回组成员
    """
    user_ids = GroupUser.objects.filter(group_id=group_id).values_list("user_id", flat=True)
    users = User.objects.filter(id__in=user_ids)
    user_list = []
    sign = request.GET.get("sign")
    if sign == "0":
        group = Group.objects.get(id=group_id)
        admin_usernames = group.admin_list
        users = users.exclude(username__in=admin_usernames)
    for user in users:
        user_list.append(
            {"id": user.id, "username": user.username, "name": user.name, "phone": user.phone, "email": user.email}
        )
    return JsonResponse({"result": True, "code": 0, "message": "查询成功", "data": user_list})


def exit_group(request, group_id):
    """组内移除用户（可能不是当前用户），用户退出组"""
    req = json.loads(request.body)
    params = {"user_id": "用户id"}
    check_result, message = check_param(params, req)
    if not check_result:
        return JsonResponse({"result": False, "code": 1, "message": message})
    user_id = req.get("user_id")
    try:
        GroupUser.objects.get(group_id=group_id, user_id=user_id).delete()
    except GroupUser.DoesNotExist:
        return JsonResponse({"result": False, "code": 1, "message": "该用户不在组中"})
    return JsonResponse({"result": True, "code": 0, "message": "移除成功", "data": []})


@require_http_methods(["GET"])
@is_group_member(admin_needed=["GET"])
def list_group_admin(request, group_id):
    """
    获取组内管理员列表
    """
    # 组内成员
    try:
        admins = Group.objects.get(id=group_id).admin_list
    except Group.DoesNotExist:
        return JsonResponse({"result": False, "code": 1, "message": "组不存在", "data": []})
    return JsonResponse({"result": True, "code": 0, "message": "", "data": admins})


@require_http_methods(["GET"])
def list_admin_group(request):
    """
    获取有权限管理的所有组
    """
    # 所有加入的组
    groups = Group.objects.filter(
        id__in=GroupUser.objects.filter(user_id=request.user.id).values_list("group_id", flat=True)
    )

    # 所有管理的组
    admin_groups = []
    for g in groups:
        if request.user.username in g.admin_list:
            admin_groups.append(g.to_json())
    return JsonResponse({"result": True, "code": 0, "manage": "", "data": admin_groups})


@is_group_member(admin_needed=["POST"])
def check_user_in_group(request, group_id):
    # 查询成员是否已加入指定小组，返回未加入小组的成员姓名
    user_name = json.loads(request.body).get("UserName")
    # 待查询姓名列表
    user_name_list = str(user_name).split(" ")
    id_list = GroupUser.objects.filter(group_id=group_id).values_list("user_id", flat=True)
    joined_user_name_list = User.objects.filter(id__in=id_list).values_list("name", flat=True)
    unjoined_users = []
    for u in user_name_list:
        if u not in joined_user_name_list:
            unjoined_users.append(u)
    if len(unjoined_users) > 0:
        return JsonResponse({"result": True, "code": 0, "message": "", "data": ",".join(unjoined_users) + "未加入当前小组"})
    return JsonResponse({"result": True, "code": 0, "message": "", "data": "查询的用户已加入当前小组中"})


@require_http_methods(["POST"])
@is_group_member(admin_needed=["POST"])
def add_user(request, group_id):
    """添加用户信息"""
    req = json.loads(request.body)
    new_user_ids = set(req.get("new_user_ids"))
    # 获取日报数据库中没有的用户，将其信息从蓝鲸平台拉取过来
    sign_in_user_ids = set(User.objects.filter(id__in=new_user_ids).values_list("id", flat=True))
    user_not_in_platform = new_user_ids - sign_in_user_ids
    # ↓↓↓当有不在本系统中的用户时去主平台拉取------------
    if len(user_not_in_platform):
        client = get_client_by_request(request=request)
        response = client.usermanage.list_users(
            lookup_field="id",
            exact_lookups=",".join(map(str, user_not_in_platform)),  # 将set中的整数拼接成","连接的字符串，用做从蓝鲸平台精准获取用户信息
            fields="id,username,display_name,email,telephone",
            page=1,
            pageSize=len(user_not_in_platform),
        )
        if not response.get("result"):
            return JsonResponse({"result": False, "code": 1, "message": "从蓝鲸主平台拉取用户时出现错误"})
        # 从蓝鲸主平台拿到的新用户
        user_infos = response.get("data").get("results")
        # 将新用户添加到数据库
        new_users = []
        for u_info in user_infos:
            new_users.append(
                User(
                    id=u_info["id"],
                    username=u_info["username"],
                    name=u_info["display_name"],
                    email=u_info["email"],
                    phone=u_info["telephone"],
                )
            )
        User.objects.bulk_create(new_users)
    # ↑↑↑拉取成功-----------------------------------

    # 添加组-用户表
    new_group_user = []
    for user_id in new_user_ids:
        new_group_user.append(GroupUser(user_id=user_id, group_id=group_id))
    GroupUser.objects.bulk_create(new_group_user)
    return JsonResponse({"result": True, "code": 0, "message": "添加用户成功", "data": []})
