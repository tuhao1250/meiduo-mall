from django.shortcuts import render

# Create your views here.
import os

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from alipay import AliPay
from orders.models import OrderInfo
from django.conf import settings
from .models import Payment


class AlipayView(APIView):
    """支付宝支付视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        """获取支付宝链接地址"""
        # 获取order_id
        # 查询order_id是否存在,获取订单金额
        try:
            order = OrderInfo.objects.get(
                oid=order_id,
                user=request.user,
                pay_method=OrderInfo.PAY_METHOD_ENUM['ALIPAY'],
                status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except OrderInfo.DoesNotExist:
            return Response({"message": "订单信息有误"})
        # 构造支付宝支付链接地址
        alipay_client = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keys/app_private_key.pem'),
            # 支付宝的公钥
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keys/alipay_public_key.pem'),
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG  # 默认False
        )
        # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
        order_string = alipay_client.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_amount),
            subject="美多商城%s" % order_id,
            return_url="http://www.meiduo.site:8080/pay_success.html",
        )
        # 向前端返回链接地址
        alipay_url = settings.ALIPAY_URL + "?" + order_string
        return Response({"alipay_url": alipay_url})


class SavePaymentView(APIView):
    """保存支付宝支付结果视图"""
    permission_classes = [IsAuthenticated]

    def put(self, request):
        """保存信息"""
        # 获取支付宝传递的参数
        # 将参数的querydict转换成字典
        data = request.query_params.dict()
        # 从参数中剔除sign字段,
        signature = data.pop('sign')
        # 比较sign的值和剩余字段加密后的结果是否相同,相同才说明是支付宝发送的数据
        alipay_client = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keys/app_private_key.pem'),
            # 支付宝的公钥
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keys/alipay_public_key.pem'),
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG  # 默认False
        )
        success = alipay_client.verify(data, signature)
        if not success:
            # 请求不是从支付宝发送的,返回非法的请求
            return Response({"message": "非法的请求"}, status=status.HTTP_403_FORBIDDEN)
        # 获取参数中的支付宝交易流水号
        trade_id = data.get('trade_no')
        order_id = data.get('out_trade_no')
        # 校验订单id
        try:
            order = OrderInfo.objects.get(oid=order_id, user=request.user, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except OrderInfo.DoesNotExist:
            return Response({"message": "订单信息有误"}, status=status.HTTP_400_BAD_REQUEST)
        # 保存数据到数据库中
        # 添加订单支付记录
        Payment.objects.create(order=order, trade_id=trade_id)
        # 更新订单状态
        order.status = OrderInfo.ORDER_STATUS_ENUM['UNSEND']
        order.save()
        # 向前端返回支付宝交易流水号
        return Response({"trade_id": trade_id})

