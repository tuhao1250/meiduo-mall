from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework_extensions.cache.mixins import CacheResponseMixin
from .serializers import AreaSerializer, SubAreaSerializer
from .models import Area

# Create your views here.


class AreaViewSet(CacheResponseMixin, ModelViewSet):
    """
    行政区划视图集
    list:
    返回行政区划顶级行政区域数据

    retrieve:
    返回顶级行政区划或市级行政区划关联的下属行政区划数据
    """
    pagination_class = None

    def get_serializer_class(self):
        """根据请求不同,返回不同的序列化器"""
        if self.action == "list":
            # 请求的单一数据
            return AreaSerializer
        else:
            return SubAreaSerializer

    def get_queryset(self):
        """重写获取查询集的方法"""
        if self.action == "list":
            # 请求的是顶级省份区域信息
            return Area.objects.filter(parent=None)
        else:
            return Area.objects.all()
