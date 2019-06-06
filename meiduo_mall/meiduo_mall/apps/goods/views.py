from django.shortcuts import render
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_extensions.cache.mixins import ListCacheResponseMixin
from rest_framework.filters import OrderingFilter
from drf_haystack.viewsets import HaystackViewSet

from .serializers import SKUSerializer, SKUIndexSerializer
from .models import SKU, GoodsCategory, GoodsChannel
from . import constants

# Create your views here.


class HotSKUListView(ListCacheResponseMixin, ListAPIView):  # 添加缓存
    """
    热销SKU商品视图
    GET /categories/<int:category_id>/hotskus/
    """
    serializer_class = SKUSerializer
    pagination_class = None

    def get_queryset(self):
        """
        重写获取queryset方法
        :return:
        """
        # 获取url中的category_id
        category_id = self.kwargs.get('category_id')
        return SKU.objects.filter(category_id=category_id, is_launched=True).order_by('-sales')[:constants.HOT_SKU_COUNT_LIMIT]


class SKUListView(ListAPIView):
    """
    SKU商品列表页视图
    GET /categories/<int:category_id>/skus?page=xxx&page_size=xxx&ordering=xxx
    """
    serializer_class = SKUSerializer
    # 排序的支持需要使用OrderingFilter过滤器后端
    filter_backends = [OrderingFilter]
    # 指明排序的字段
    ordering_fields = ['create_time', 'price', 'sales']

    def get_queryset(self):
        """获取查询集"""
        # 获取前端传递的商品类别
        category_id = self.kwargs.get('category_id')
        return SKU.objects.filter(category_id=category_id, is_launched=True)


class CatView(APIView):
    """
    商品分类视图
    GET /categories/<int:cat_id>/'
    """
    def get(self, request, cat_id):
        """
        根据三级类别id获取对应的一级类别,二级类别,三级类别
        :param request
        :param cat_id:
        :return:
        """
        # cat_id = self.kwargs['cat_id']
        try:
            cat3 = GoodsCategory.objects.get(id=cat_id)
        except GoodsCategory.DoesNotExist:
            return Response({"message": "类别不存在"}, status=status.HTTP_400_BAD_REQUEST)
        cat2 = cat3.parent
        cat1 = cat2.parent
        # 根据顶级类别cat1获取商品频道
        channel = GoodsChannel.objects.get(category=cat1)
        cat3_dict = {
            "id": cat3.id,
            "name": cat3.name
        }
        cat2_dict = {
            "id": cat2.id,
            "name": cat2.name
        }
        cat1_dict = {
            "url": channel.url,
            "category": {
                "id": cat1.id,
                "name": cat1.name
            }
        }
        return Response({
            "cat1": cat1_dict,
            "cat2": cat2_dict,
            "cat3": cat3_dict,
        })


class SKUSearchViewSet(HaystackViewSet):
    """
    SKU搜索
    """
    index_models = [SKU]
    serializer_class = SKUIndexSerializer
