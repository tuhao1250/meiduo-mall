from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import pickle
import base64
from .serializers import UserCartSerializer, CartSKUSerializer
from . import constants
from goods.models import SKU


class CartView(APIView):
    """购物车视图"""
    def perform_authentication(self, request):
        """重写验证用户身份函数"""
        # 前端不会判断用户是否登录,无论是否登录都会传递一个JWT token,传递错误的token的请求会被拒绝,为了不让请求被拒,这里不做任何处理
        pass

    def get(self, request):
        # 前端不需要额外传递参数,对于登录用户,购物车数据会通过用户id从redis获取,对于未登录用户,购物车数据从cookie中读取
        # 判断用户是否登录
        try:
            user = request.user
        except Exception as e:
            user = None
        if user is not None and user.is_authenticated:
            # 用户已登录
            # 查询redis中两个值,一个是hash,一个是set
            redis_conn = get_redis_connection('cart')
            # hgetall(name) -> dict
            # cart_date = {"sku_id1": "2", "sku_id2": "1"}
            cart_data = redis_conn.hgetall('cart_%s' % user.id)
            cart_selected = redis_conn.smembers('cart_selected_%s' % user.id)
            # 将redis中的两个数据合并为类似cookie中的数据
            cart_dict = {}
            for sku_id, count in cart_data.items():
                # 注意python3从redis中获取的都是字节
                # cart_dict[int(sku_id)]['count'] = int(count)
                # cart_dict[int(sku_id)]['selected'] = sku_id in cart_selected
                cart_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in cart_selected
                }
        else:
            # 用户未登录, 从cookie中读取
            cookie_cart = request.COOKIES.get('cart')
            if cookie_cart:
                # cookie中存在
                cart_dict = pickle.loads(base64.b64decode(cookie_cart))
            else:
                cart_dict = {}
        # 从cart_dict中获取sku_ids
        sku_ids = cart_dict.keys()
        skus = SKU.objects.filter(id__in=sku_ids)
        # 注意,数据库中查询的数据没有count和select属性,需要手动补充
        for sku in skus:
            sku.count = cart_dict[sku.id]['count']
            sku.selected = cart_dict[sku.id]['selected']

        # 使用序列化器序列化数据
        serializer = CartSKUSerializer(instance=skus, many=True)
        return Response(serializer.data)

    def post(self, request):
        """新增购物车记录"""
        # 获取前端传递的数据,使用序列化器进行校验
        selected = request.data.get('selected')
        serializer = UserCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 获取验证后的数据
        sku_id = serializer.validated_data['sku_id']
        count = serializer.validated_data['count']
        selected = serializer.validated_data['selected']
        # 保存购物车数据
        # 判断用户是否登录,如果已经登录,就保存到redis中,如果没有登录就保存的cookie中
        try:
            user = request.user
        except Exception as e:
            user = None
        if user is not None and user.is_authenticated:
            # 用户已登录
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()
            # 存入购物车中的商品id和对应的数量,如果商品在redis中存在,就添加数量,如果不存在,就新增
            # 使用HINCRBY可以简写代码 hincrby(name, key, amount=1)
            pl.hincrby('cart_%s' % user.id, sku_id, count)
            # 存入购物车中选中的商品记录
            # 使用SADD sadd(name, *values)
            if selected:
                pl.sadd('cart_selected_%s' % user.id, sku_id)
            pl.execute()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            # 用户未登录, 保存到cookie中
            # 先从cookie中读取购物车数据
            cookie_cart = request.COOKIES.get('cart')
            if cookie_cart:
                # cookie中存在购物车记录
                # print("cookie存在")
                cart_dict = pickle.loads(base64.b64decode(cookie_cart))
                # cart_dict是一个字典{"sku_id":{"count":1, "selected":"True"}}
            else:
                # cookie中不存在购物车记录
                # print("cookie不存在")
                cart_dict = {}
            # 判断商品在cart_dict中是否存在
            if sku_id in cart_dict:
                # sku_id在cookie的购物车数据中存在,则增加数量
                count = count + cart_dict[sku_id]["count"]
            # cart_dict[sku_id]["count"] = count
            # cart_dict[sku_id]["selected"] = selected
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }
            # print(cart_dict)
            # 存储到cookie中
            # 先创建response对象
            # print("正在写入cookie")
            response = Response(serializer.data, status=status.HTTP_201_CREATED)
            response.set_cookie('cart', base64.b64encode(pickle.dumps(cart_dict)).decode(), max_age=constants.CART_COOKIE_EXPIRES)
            return response
