def check_param(params, kwargs: dict):
    """参数校验"""
    for key in params:
        if key not in kwargs or not kwargs[key]:
            return params.get(key)
