from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins
import re
from rest_framework.permissions import IsAuthenticated

from .models import User
from .serializers import CreateUserSerializer, CheckSMSCodeSerializer, ResetPasswordSerializer, UserDatailSerializer
from verifications.serializers import CheckImageCodeSerializer
from .utils import get_user_by_account
# Create your views here.


class UsernameCountView(APIView):
    """根据用户名查询用户数量的视图"""

    # GET /usernames/<username:username>/count/
    def get(self, request, username):
        """
        查询指定用户名数量
        :param request:
        :param username:
        :return:
        """
        count = User.objects.filter(username=username).count()

        data = {
            "username": username,
            "count": count
        }
        return Response(data)


class MobileCountView(APIView):
    """根据手机号查询用户数量"""

    # GET /mobiles/<mobile:mobile>/count/
    def get(self, request, mobile):
        """
        查询指定手机号码对应的用户数量
        :param request:
        :param mobile:
        :return:
        """
        count = User.objects.filter(mobile=mobile).count()
        data = {
            "mobile": mobile,
            "count": count
        }
        return Response(data)


class UserView(CreateAPIView):
    """用户注册视图"""
    serializer_class = CreateUserSerializer


class SMSCodeTokenView(GenericAPIView):
    """获取发送短信验证码的凭证视图"""
    serializer_class = CheckImageCodeSerializer

    def get(self, request, account):
        """
        获取发送短信验证码的凭证
        :param request:
        :param account:
        :return:
        """
        # 校验图片验证码
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        # 根据account查询用户对象
        user = get_user_by_account(account)
        if not user:
            # 用户不存在,则直接返回404
            return Response({'message': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
        # 根据用户对象的手机号生成access_token

        # 修改手机号,使用re.sub进行替换
        mobile = re.sub(r'(\d{3})\d{4}(\d{4})', r'\1****\2', user.mobile)
        access_token = user.generic_send_sms_code_token()
        return Response({
            'mobile': mobile,
            'access_token': access_token
        })


class PasswordTokenView(GenericAPIView):
    """获取修改密码的token视图"""
    serializer_class = CheckSMSCodeSerializer

    def get(self, request, account):
        """
        获取修改密码的token
        :param request:
        :param account:
        :return:
        """
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        user = serializer.user

        # 生成修改用户密码的access_token
        access_token = user.generate_set_password_token()
        return Response({'user_id': user.id, 'access_token': access_token})


class PasswordView(GenericAPIView):
    """用户密码视图"""

    serializer_class = ResetPasswordSerializer
    queryset = User.objects.all()

    def post(self, request, pk):
        """
        重置密码方法
        :param request:
        :param pk: user对象的主键
        :return:
        """
        instance = self.get_object()
        # 获取序列化器
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserDetailView(RetrieveAPIView):
    """用户详情视图"""
    queryset = User.objects.all()
    serializer_class = UserDatailSerializer
    # 补充只有通过认证才能访问接口的权限
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        返回请求的用户对象
        :return:
        """
        # 在类视图对象中也保存了请求对象request
        # request对象的user属性,是通过认证检验之后的请求用户对象
        # 在类视图中除了存在request对象,还存在了kwargs属性
        return self.request.user








