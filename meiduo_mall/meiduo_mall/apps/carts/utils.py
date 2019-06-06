import pickle
import base64
from django_redis import get_redis_connection


def merge_cart_cookie_to_redis(request, response, user):
    """
    用户登录时合并购物车数据到redis方法
    :param request: 请求的request对象
    :param response: 返回的响应response对象
    :param user: 登录的用户对象
    :return: response对象
    """
    # 从cookie中取出购物车数据,
    cookie_cart_str = request.COOKIES.get('cart')
    if not cookie_cart_str:
        # cookie中不存在购物车记录,不需要执行合并
        return response
    else:
        cookie_cart_dict = pickle.loads(base64.b64decode(cookie_cart_str))
        # 从redis中读取购物车数据
        # 将cookie购物车数据以覆盖的方式覆盖到redis中,覆盖指的是将cookie中的数量覆盖到对应的redis中,如果redis不存在,就插入.
        # 不影响在redis中但不在cookie中的数据
        redis_conn = get_redis_connection('cart')
        pl = redis_conn.pipeline()
        # 覆盖redis的hash可以采用hmset(name, mapping)方法,将字典的所有键值对覆盖到redis中
        # 从cookie中覆盖到redis商品数量的字典
        cookie_to_redis_dict = {}
        # 记录应该从cookie中覆盖到redis选中的商品的id列表
        redis_selected_add_sku_ids = []
        # 记录redis选中商品集合中应该被删除的商品id的列表
        redis_selected_remove_sku_ids = []
        for sku_id, count_seleted_dict in cookie_cart_dict.items():
            cookie_to_redis_dict[sku_id] = count_seleted_dict['count']
            if count_seleted_dict['selected']:
                # 如果在cookie中选中了商品,则添加到要覆盖到redis中的选中的商品id列表中
                redis_selected_add_sku_ids.append(sku_id)
            else:
                # cookie中没有选中,则redis中即使选中了,也要删除选中状态
                redis_selected_remove_sku_ids.append(sku_id)
        # 将cookie中商品数量覆盖到redis中
        pl.hmset('cart_%s' % user.id, cookie_to_redis_dict)
        # 将cookie中选中的商品覆盖到redis中
        pl.sadd('cart_selected_%s' % user.id, *redis_selected_add_sku_ids)
        pl.srem('cart_selected_%s' % user.id, *redis_selected_remove_sku_ids)
        pl.execute()
        # 删除cookie中的数据,返回应答
        response.delete_cookie('cart')
        return response

