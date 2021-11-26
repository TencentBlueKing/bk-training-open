from django.core.paginator import EmptyPage, Paginator


def check_param(params, kwargs: dict):
    """校验不可为空的参数"""
    for key in params:
        if key not in kwargs or not kwargs[key]:
            return False, u"缺少{}".format(params.get(key))
    return True, None


def get_paginator(content, page, size):
    """生成分页器"""
    lists = Paginator(content, size)
    try:
        ansPage = lists.page(page)
    except EmptyPage:
        ansPage = lists.page(lists.num_pages)
    except Exception:
        ansPage = lists.page(1)
    return ansPage
