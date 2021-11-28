def check_param(params, kwargs: dict):
    """校验不可为空的参数"""
    for key in params:
        if key not in kwargs or not kwargs[key]:
            return False, u"缺少{}".format(params.get(key))
    return True, None


def apply_info_to_json(apply_info):
    """将申请入组信息进行json转化"""
    return {
        "user_id": apply_info.id,
        "username": apply_info.username,
        "name": apply_info.name,
        "apply_date": apply_info.update_time.strftime("%Y-%m-%d %H:%M:%S"),
    }
