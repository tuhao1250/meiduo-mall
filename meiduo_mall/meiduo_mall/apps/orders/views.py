from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import OrderingFilter
import decimal
from .models import OrderInfo
from goods.models import SKU
from .serializers import OrderSettlementSerializer, SaveOrderSerializer, OrderInfoSerializer
# Create your views here.


class OrderSettlementView(APIView):
    """订单结算视图"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """获取订单结算内容"""
        # 获取user对象
        user = request.user
        # 查询redis获取购物车数据
        redis_conn = get_redis_connection('cart')
        # sku_count = {"id1":2,"id2":3}
        # 获取购物车中所有商品的数量
        sku_count_dict = redis_conn.hgetall('cart_%s' % user.id)
        # 获取购物车中选中商品的列表
        sku_selected_list = redis_conn.smembers('cart_selected_%s' % user.id)
        # 构建选中商品及数量的字典
        cart_sku = {}
        for sku_id in sku_selected_list:
            cart_sku[int(sku_id)] = int(sku_count_dict[sku_id])
        # 构建sku对象的列表
        skus = SKU.objects.filter(id__in=cart_sku.keys())
        # 为skus列表的每个对象添加count属性
        for sku in skus:
            sku.count = cart_sku[sku.id]
        # 运费
        freight = decimal.Decimal("10.00")
        # 构建序列化数据对象
        instance = {"freight": freight, "skus": skus}
        # 构建序列化器
        serializer = OrderSettlementSerializer(instance)
        # 返回
        return Response(serializer.data)


class SaveOrderView(CreateAPIView):
    """保存订单视图"""

    permission_classes = [IsAuthenticated]
    serializer_class = SaveOrderSerializer


class OrdersAllView(ListAPIView):
    """用户全部订单视图"""

    permission_classes = [IsAuthenticated]
    serializer_class = OrderInfoSerializer
    # # 排序的支持需要使用OrderingFilter过滤器后端
    # filter_backends = [OrderingFilter]
    # # 指明排序的字段
    # ordering_fields = ['create_time']

    def get_queryset(self):
        # 获取该用户所有订单
        orders = OrderInfo.objects.filter(user=self.request.user).order_by("-create_time")
        return orders
