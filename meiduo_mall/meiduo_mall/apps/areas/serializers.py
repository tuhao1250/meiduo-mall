from rest_framework import serializers
from .models import Area


class AreaSerializer(serializers.ModelSerializer):
    """顶级行政区划序列化器"""

    class Meta:
        model = Area
        fields = ['id', 'name']


class SubAreaSerializer(serializers.ModelSerializer):
    """子级行政区域序列化器"""

    # 返回的是多个,所以要many=True,仅用于序列化
    subs = AreaSerializer(many=True, read_only=True)  # 因为这个序列化器直接返回的就是id和name,正好就是需求里需要返回的数据.

    class Meta:
        model = Area
        fields = ['id', 'name', 'subs']  # subs=>area_set,通过related_name取代了默认的类名_set获取关联的多端对象的方法

