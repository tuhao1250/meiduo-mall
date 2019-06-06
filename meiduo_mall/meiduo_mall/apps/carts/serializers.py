from rest_framework import serializers

from goods.models import SKU


class UserCartSerializer(serializers.Serializer):
    """用户购物车数据序列化器"""

    sku_id = serializers.IntegerField(min_value=1, label="商品SKUid", help_text="SKU_ID")
    count = serializers.IntegerField(min_value=1, label="商品数量", help_text="商品数量")
    selected = serializers.BooleanField(default=True, label="是否勾选", help_text="商品勾选状态")

    def validate(self, attrs):
        """校验数据"""
        sku_id = attrs['sku_id']
        count = attrs['count']
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            raise serializers.ValidationError("商品不存在")
        # 比较商品库存与count的大小
        if sku.stock < count:
            raise serializers.ValidationError("商品库存不足")
        return attrs


class CartSKUSerializer(serializers.ModelSerializer):
    """购物车商品序列化器"""
    count = serializers.IntegerField(label="购物车单个商品数量", help_text="购物车单个商品数量")
    selected = serializers.BooleanField(label="购物车单个商品是否选中", help_text="购物车中单个商品是否选中")

    class Meta:
        model = SKU
        fields = ['id', 'count', 'default_image_url', 'price', 'name', 'selected']