from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_jwt.settings import api_settings

from carts.utils import merge_cart_cookie_to_redis
from .utils import OAuthQQ
from .exceptions import QQAPIException
from .models import OAuthQQUser
from .serializers import OAuthQQUserSerializer


# Create your views here.


class OAuthQQURLView(APIView):
    """
    提供QQ登录的网址,
    前端请求的接口网址 /oauth/qq/authorization/?state=xxxx
    state参数由前端传递,参数值为在QQ登录后,我们后端把用户引导到美多商城的哪个页面
    """
    def get(self, request):
        """
        获取QQ登录的网址
        :param request:
        :return:
        """
        # 提取state参数
        state = request.query_params.get('next', '/')
        # if not state:
        #     state = '/'  # 如果前端未指明,后端设置用户QQ登录成功后,跳转到首页
        # 按照QQ的说明文档,拼接用户QQ登录的链接地址
        oauth_qq = OAuthQQ(state=state)
        login_url = oauth_qq.generate_qq_login_url()

        # 返回链接地址
        return Response({"oauth_url": login_url})


class OAuthQQUserView(GenericAPIView):
    """
    获取QQ用户对应美多商城用户
    """
    serializer_class = OAuthQQUserSerializer

    def get(self, request):
        """获取QQ用户对应美多商城用户"""
        # 提取code参数
        code = request.query_params.get('code')
        if not code:
            return Response({'message': '缺少code'}, status.HTTP_400_BAD_REQUEST)
        # state = request.query_params.get('state')
        # 向QQ服务器发送请求,获取access_token
        oauth_qq = OAuthQQ()
        try:
            access_token = oauth_qq.get_access_token(code)
            # 凭借access_token,向QQ服务器发送请求,获取QQ用户的open_id
            openid = oauth_qq.get_open_id(access_token)
        except QQAPIException:
            return Response({'message': '获取QQ用户数据异常'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        # 根据openid查询用户是否绑定过美多商城的用户
        try:
            oauth_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 如果未绑定,手动创建接下来绑定身份使用的access_token,是根据openid使用itsdangerous加密生成的
            access_token = OAuthQQUser.generate_save_user_token(openid)
            return Response({'access_token': access_token})
        # 如果已经绑定过,直接生成登录JWT token并返回
        user = oauth_user.user
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        response = Response({
            'token': token,
            'username': user.username,
            'user_id': user.id
        })
        # 合并购物车
        response = merge_cart_cookie_to_redis(request, response, user)
        return response

    def post(self, request):
        """
        QQ用户登录后,绑定美多商城用户
        :param request:
        :return: user_id, user_name, token
        """
        # 执行反序列化的第一步
        serializer = self.get_serializer(data=request.data)
        # 使用序列化器校验数据
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # 生成JWT token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        response = Response({
            'token': token,
            'username': user.username,
            'user_id': user.id
        })
        # 合并购物车
        response = merge_cart_cookie_to_redis(request, response, user)
        return response















