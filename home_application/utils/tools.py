from django.core.paginator import Paginator

from home_application.models import Group, GroupUser


def check_param(params, kwargs: dict):
    """校验不可为空的参数"""
    for key in params:
        if key not in kwargs or not kwargs[key]:
            return False, u"缺少{}".format(params.get(key))
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
    group_ids = GroupUser.objects.filter(user_id=request.user.id).values_list("group_id", flat=True)
    user_name = request.user.username
    groups = Group.objects.filter(id__in=group_ids)
    if check_type == 0:
        for g in groups:
            if user_name not in g.admin_list:
                return False
        return True
    else:
        for g in groups:
            if user_name in g.admin_list:
                return True
        return False
