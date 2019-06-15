from django_redis import get_redis_connection
from rest_framework import serializers
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from goods.models import SKU
from django.db import transaction
import decimal
import time
import logging
from . models import OrderInfo, OrderGoods


logger = logging.getLogger('django')


class CartSKUSerializer(serializers.ModelSerializer):
    """购物车商品序列化器"""

    count = serializers.IntegerField(label='数量')

    class Meta:
        model = SKU
        fields = ['id', 'default_image_url', 'price', 'count', 'name']


class OrderSettlementSerializer(serializers.Serializer):
    """订单结算序列化器"""

    freight = serializers.DecimalField(label="运费", max_digits=11, decimal_places=2)
    skus = CartSKUSerializer(many=True)


class SaveOrderSerializer(serializers.ModelSerializer):
    """保存订单序列化器"""

    class Meta:
        model = OrderInfo
        fields = ['oid', 'address', 'pay_method']
        read_only_fields = ['oid']
        extra_kwargs = {
            "address": {
                'write_only': True,
                'required': True
            },
            'pay_method': {
                'write_only': True,
                'required': True
            }
        }

    def create(self, validated_data):
        """保存订单的函数"""
        # 获取下单用户
        user = self.context['request'].user
        # 获取下单选择的地址
        address = validated_data['address']
        # print(address)  # 这里是一个Address object
        # 获取pay_method
        pay_method = validated_data['pay_method']
        # 生成运费,实际项目中可能会是根据总金额去某张表中取运费金额
        freight = decimal.Decimal('10.00')
        # 生成订单编号
        # timezone.now()=>datetime.datetime(2019, 6, 12, 1, 45, 51, 677837, tzinfo=<UTC>)
        order_id = timezone.now().strftime('%Y%m%d%H%M%S') + '%09d' % user.id
        # 保存OrderInfo, 从这里开始需要开启事物
        with transaction.atomic():
            # 创建一个保存点(保存订单基本信息的保存点)
            save_order_info = transaction.savepoint()
            try:
                order = OrderInfo.objects.create(
                    oid=order_id,
                    user=user,
                    address=address,
                    total_count=0,
                    total_amount=decimal.Decimal(0),
                    freight=freight,
                    pay_method=pay_method,
                    status=OrderInfo.ORDER_STATUS_ENUM['UNSEND'] if pay_method == OrderInfo.PAY_METHOD_ENUM["CASH"] else OrderInfo.ORDER_STATUS_ENUM["UNPAID"]
                )
                # 从redis中取出购物车数据,获取下单商品skuid,price,count
                redis_conn = get_redis_connection('cart')
                # redis_cart = {"id1":2,"id2":3}
                redis_cart = redis_conn.hgetall('cart_%s' % user.id)
                redis_selected = redis_conn.smembers('cart_selected_%s' % user.id)
                order_cart = {}
                # order_cart = {sku_id1:count,...}
                for sku_id in redis_selected:
                    order_cart[int(sku_id)] = int(redis_cart[sku_id])
                # 获取要下单的sku_id列表对应的sku商品的列表
                # skus = SKU.objects.filter(id__in=order_cart.keys())
                # 遍历商品列表,判断每个商品的库存是否充足
                for sku_id in order_cart.keys():
                    while True:
                        sku = SKU.objects.get(id=sku_id)
                        # 订单数量
                        order_count = order_cart[sku_id]
                        # 原始库存数量
                        origin_stock = sku.stock
                        # 原始销量
                        origin_sales = sku.sales
                        # 判断商品库存是否充足
                        if order_count > origin_stock:
                            # 订单数量大于库存量,抛出异常,因为是在序列化器内抛出异常,不能返回400
                            # 抛出异常之前需要先返回到保存点
                            transaction.savepoint_rollback(save_order_info)
                            raise ValidationError("库存量不足")
                        # time.sleep(5)  # 用于模拟订单并发
                        # 减少库存,增加销量
                        now_stock = origin_stock - order_count
                        now_sales = origin_sales + order_count
                        # # 设置商品库存和销量
                        # sku.stock = now_stock
                        # sku.sales = now_sales
                        # ret是执行更新操作受影响的行数
                        # SKU.object.select_for_update().filter()使用悲观锁枷锁的方式,直到事物结束,才会解锁
                        # print("当前原始库存%d" % origin_stock)
                        ret = SKU.objects.filter(id=sku.id, stock=origin_stock).update(stock=now_stock, sales=now_sales)
                        # 判断受影响的行数是否等于0就知道是否有执行过更新操作
                        # print("ret=%d" % ret)
                        if ret == 0:
                            # 为更新成功,说明有人抢先下单了
                            continue
                        # sku.save()  为什么加上这句话导致每次下了订单库存量没有变化了呢?

                        # 增加商品spu的销量
                        sku.goods.sales += order_count
                        sku.goods.save()

                        # 累计订单基本信息表中total_count和total_amount
                        order.total_count += order_count
                        order.total_amount += (order_count * sku.price)

                        # 保存OrderGoods
                        OrderGoods.objects.create(order=order, sku=sku, price=sku.price, count=order_count)
                        # 执行完一次更新就跳出循环
                        break
                # 注意订单总金额还需要加上运费
                order.total_amount += freight
                order.save()
                # 整体提交事务
                transaction.savepoint_commit(save_order_info)
            except ValidationError:
                # 由于出现这个遗产的时候已经做了回滚,这里不能再回滚了
                raise
            except Exception as e:
                logger.error(e)
                # 抛出异常之前需要回滚数据库
                transaction.savepoint_rollback(save_order_info)
                raise

        # 删除购物车中已经下单的数据
        pl = redis_conn.pipeline()
        pl.hdel('cart_%s' % user.id, *redis_selected)
        pl.srem('cart_selected_%s' % user.id, *redis_selected)
        pl.execute()
        return order


class GoodsSKUSerializer(serializers.ModelSerializer):
    """商品SKU序列化器"""

    class Meta:
        model = SKU
        fields = ['id', 'name', 'default_image_url', 'price']


class OrderGoodsSerializer(serializers.ModelSerializer):
    """订单商品序列化器"""
    sku = GoodsSKUSerializer(read_only=True)

    class Meta:
        model = OrderGoods
        fields = ['count', 'price', 'sku', 'is_commented']


class OrderInfoSerializer(serializers.ModelSerializer):
    """用户订单序列化器"""
    skus = OrderGoodsSerializer(many=True, read_only=True)
    create_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = OrderInfo
        fields = ['oid', 'create_time', 'total_amount', 'freight', 'pay_method', 'status', 'skus']