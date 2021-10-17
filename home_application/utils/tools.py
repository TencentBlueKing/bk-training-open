def check_param(params, kwargs: dict):
    """校验不可为空的参数"""
    for key in params:
        if key not in kwargs or not kwargs[key]:
            return False, u"缺少{}".format(params.get(key))
    return True, None


def group2json(group):
    """将Group转化为json str的格式"""
    return {
        "id": group.id,
        "name": group.name,
        "admin": group.admin,
    }


def user2json(user):
    """将User转化为json str的格式"""
    return {
        "id": user.id,
        "username": user.username,
        "name": user.name,
        "phone": user.phone,
        "email": user.email,
    }

