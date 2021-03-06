import math

from django.core.paginator import Paginator

from blueapps.utils import get_client_by_request
from home_application.models import Group, GroupUser


def check_param(params, kwargs: dict):
    """校验不可为空的参数"""
    for key in params:
        if key not in kwargs or not kwargs[key]:
            return False, "缺少{}".format(params.get(key))
    return True, None


def get_paginator(objects, page, size):
    """生成分页器"""
    p = Paginator(objects, size)
    try:
        return p.page(page)
    except Exception:
        return None


def apply_info_to_json(apply_info):
    """将申请入组信息进行json转化"""
    return {
        "user_id": apply_info.id,
        "username": apply_info.username,
        "name": apply_info.name,
        "apply_date": apply_info.update_time.strftime("%Y-%m-%d %H:%M:%S"),
    }


def apply_is_available_to_json(group):
    """是否可申请入组，组信息进行json转化"""
    return {"id": group.id, "group_name": group.name, "is_available": group.is_available}


def check_user_is_admin(request, check_type):
    """
    check_type为0时，判断用户是否在其所加入的所有组皆为管理员，若是返回True，反之返回False;
    check_type为1时，判断用户是否在其所加入的所有组中，至少是其中一个组的管理员，若是返回True，反之返回False
    """
    user_name = request.user.username
    # 所有加入的组id
    group_ids = set(GroupUser.objects.filter(user_id=request.user.id).values_list("group_id", flat=True))
    # 所有管理的组
    groups = Group.objects.filter(id__in=group_ids)
    manage_group_ids = {g.id for g in groups if user_name in g.admin_list}
    if check_type == 0:
        return group_ids == manage_group_ids
    else:
        return len(manage_group_ids) > 0


def bulk_load_bk_users(request):
    client = get_client_by_request(request=request)
    response = client.usermanage.list_users(fields="id,username,display_name", page=1, pageSize=1)
    result = response.get("result")
    if not result:
        return False, response, 0
    count = response.get("data").get("count")
    total_page = math.ceil(count / 50)
    data = response.get("data").get("results")
    for page in range(2, total_page + 1):
        response = client.usermanage.list_users(fields="id,username,display_name", page=page, pageSize=100)
        result = response.get("result")
        if result:
            data.extend(response.get("data").get("results"))
        else:
            return False, response, 0
    return True, data, count
