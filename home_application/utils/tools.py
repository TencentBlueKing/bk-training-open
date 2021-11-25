from django.core.paginator import EmptyPage, InvalidPage, PageNotAnInteger, Paginator


def check_param(params, kwargs: dict):
    """校验不可为空的参数"""
    for key in params:
        if key not in kwargs or not kwargs[key]:
            return False, u"缺少{}".format(params.get(key))
    return True, None


def get_paginator(content, pages, nums):
    """生成分页器"""
    lists = Paginator(content, nums)
    try:
        ansPage = lists.page(pages)
    except EmptyPage:
        ansPage = lists.page(lists.num_pages)
    except PageNotAnInteger:
        ansPage = lists.page(1)
    except InvalidPage:
        ansPage = lists.page(1)
    except ValueError:
        ansPage = lists.page(1)
    return ansPage
