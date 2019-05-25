from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from .models import User
from .serializers import CreateUserSerializer
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
