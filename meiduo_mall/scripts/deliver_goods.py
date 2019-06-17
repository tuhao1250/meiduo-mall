#!/usr/bin/env python

"""
手动生成所有sku详情静态页面的脚本
使用方法:
    ./deliver_goods.py
"""

import sys

# 添加导报路径
sys.path.insert(0, '../')
sys.path.insert(0, '../meiduo_mall/apps')

# 设置django运行所依赖的环境变量
import os

if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'


# django初始化
import django
django.setup()

from orders.models import OrderInfo


def update_order_status():
    """更新订单状态函数"""
    # 查询数据库,获取所有状态为待发货的商品
    unsend_orders = OrderInfo.objects.filter(status=OrderInfo.ORDER_STATUS_ENUM['UNSEND'])
    for order in unsend_orders:
        # 如果支付方式是支付宝的,就把状态更新为待评价,
        if order.pay_method == OrderInfo.PAY_METHOD_ENUM['ALIPAY']:
            order.status = OrderInfo.ORDER_STATUS_ENUM['UNCOMMENT']
        elif order.pay_method == OrderInfo.PAY_METHOD_ENUM['CASH']:
            # 如果支付方式是货到付款的,就把状态改为待支付
            order.status = OrderInfo.ORDER_STATUS_ENUM['UNPAID']
        order.save()


if __name__ == "__main__":
    update_order_status()