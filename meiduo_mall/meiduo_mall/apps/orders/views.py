from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, ListAPIView, GenericAPIView
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
import decimal

from goods.serializers import SKUSerializer
from .models import OrderInfo, OrderGoods, SKUComments
from goods.models import SKU
from .serializers import OrderSettlementSerializer, SaveOrderSerializer, OrderInfoSerializer, OrderGoodsSerializer,\
    SKUCommentSerializer
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


class UncommentGoodsView(APIView):
    """获取未评论商品视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        # try:
        #     oredr = OrderInfo.objects.get(oid=order_id)
        # except OrderInfo.DoesNotExist:
        #     return Response({"message": "订单编号不存在"}, status=status.HTTP_400_BAD_REQUEST)
        orderGoods = OrderGoods.objects.filter(order_id=order_id, is_commented=False)
        serializer = OrderGoodsSerializer(orderGoods, many=True)
        return Response(serializer.data)


class SKUCommentView(mixins.CreateModelMixin, GenericAPIView):
    """
    商品评论视图
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    # # 排序的支持需要使用OrderingFilter过滤器后端
    # filter_backends = [OrderingFilter]
    # # 指明排序的字段
    # ordering_fields = ['create_time', 'total_comments']

    # def get_queryset(self):
    #     if self.action == 'listbysku':
    #         # 如果按照sku筛选
    #         sku_id = self.request.data['sku']
    #         # 默认按照创建日期倒序排序
    #         return SKUComments.objects.filter(sku_id=sku_id).order_by('-create_time')
    #     else:
    #         sku_id = self.request.data['sku']
    #         # 这样写太麻烦
    #         return

    def get_serializer_class(self):
        return SKUCommentSerializer

    def post(self, request, sku_id):
        """添加评论"""
        return self.create(request, sku_id)

    def get(self, request, sku_id):
        # 支持按照两种方式查询,默认按照spu筛选出所有相关的评论,
        # 获取是否勾选了只显示当前商品的评论
        sku = SKU.objects.get(id=sku_id)
        if not sku:
            return Response({'message': "商品不存在"})
        show_sku = request.query_params.get('show_sku')
        # 默认按照spu来筛选
        comments = SKUComments.objects.filter(sku=sku) if show_sku else SKUComments.objects.filter(goods=sku.goods)
        serialzier = self.get_serializer(comments, many=True)
        return Response(serialzier.data)






