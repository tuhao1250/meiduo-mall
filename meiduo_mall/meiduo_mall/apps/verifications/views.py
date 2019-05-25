from django.shortcuts import render
from django.http.response import HttpResponse
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from django_redis import get_redis_connection
import random

from meiduo_mall.libs.captcha.captcha import captcha
from . import constants
from . import serializers
from celery_tasks.sms.tasks import send_sms_code
# Create your views here.


class ImageCodeView(APIView):
    """
    获取图片验证码视图
    """

    # GET /image_codes/<str:image_code_id>/
    def get(self, request, image_code_id):
        """
        获取图片验证码方法
        :param request: 包含请求信息的对象
        :param image_code_id: 前端传递的图片验证码编号
        :return: 生成的图片文件
        """
        # 生成验证码图片
        name, text, image = captcha.generate_captcha()
        # 获取redis的连接
        redis_conn = get_redis_connection("verify_codes")  # 返回redis连接对象
        redis_conn.setex("img_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
        return HttpResponse(image, content_type="images/jpg")


class SMSCodeView(GenericAPIView):
    """获取短信验证码视图"""
    # 视图使用的序列化器
    serializer_class = serializers.CheckImageCodeSerializer

    # GET /sms_codes/<mobile:mobile>/
    def get(self, request, mobile):
        """
        获取短信验证码
        :param request: 请求对象
        :param mobile: 用户手机号
        :return:
        """
        # 获取序列化器对象
        serializer = self.get_serializer(data=request.query_params)
        # 使用序列化器对数据进行校验
        serializer.is_valid(raise_exception=True)
        # 校验通过
        # 生成短信验证码
        sms_code = '%06d' % random.randint(0, 999999)  # 生成随机六位数
        # 获取redis连接
        redis_conn = get_redis_connection('verify_codes')
        # 保存短信验证码
        # redis_conn.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 保存发送记录
        # redis_conn.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        # 创建redis管道
        pl = redis_conn.pipeline()
        # 使用管道接收命令
        pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        # 使用管道执行命令
        pl.execute()
        # 发送短信
        # ccp = CCP()
        # time = str(constants.SMS_CODE_REDIS_EXPIRES / 60)
        # ccp.send_template_sms(mobile, [sms_code, time], constants.SMS_CODE_TEMP_ID)
        # 使用celery发送异步任务
        send_sms_code.delay(mobile, sms_code)

        # 返回
        return Response({'message': 'OK'})