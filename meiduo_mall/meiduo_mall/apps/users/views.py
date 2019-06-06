from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveAPIView, UpdateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from django_redis import get_redis_connection
import re
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework_jwt.views import ObtainJSONWebToken

from .models import User, Address
from goods.models import SKU
from .serializers import CreateUserSerializer, CheckSMSCodeSerializer, ResetPasswordSerializer, \
    UserDatailSerializer, EmailSerializer, AddressSerializer, AddressTitleSerializer, AddUserHistorySerializer
from verifications.serializers import CheckImageCodeSerializer
from .utils import get_user_by_account
from . import constants
from goods.serializers import SKUSerializer
from carts.utils import merge_cart_cookie_to_redis
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
    """用户详情页视图"""
    queryset = User.objects.all()
    serializer_class = UserDatailSerializer
    # 补充只有通过认证才能访问接口的权限
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_object(self):
        """
        返回请求的用户对象
        :return:
        """
        # 在类视图对象中也保存了请求对象request
        # request对象的user属性,是通过认证检验之后的请求用户对象
        # 在类视图中除了存在request对象,还存在了kwargs属性
        return self.request.user


class EmailView(UpdateAPIView):
    """
    保存邮箱
    """
    serializer_class = EmailSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    # def get_serializer(self, *args, **kwargs):
    #     return EmailSerializer(self.request.user, data=self.request.data)


class EmailVerifyView(APIView):
    """激活邮箱"""

    def get(self, request):
        token = request.query_params.get('token')
        if not token:
            return Response({'message': '缺少token'}, status=status.HTTP_400_BAD_REQUEST)
        # 检验token,并激活链接
        result = User.check_verify_email_token(token)
        if not result:
            return Response({'message': '无效的激活链接'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'OK'})


class AddressViewSet(ModelViewSet):
    """
    地址视图
    list:
    查询用户关联的所有地址

    retrieve:
    查询用户关联的特定的地址

    create:
    添加用户收货地址

    update:
    更新用户收货地址

    destory:
    删除用户指定的收货地址

    set_default:
    设置收货地址为用户默认收货地址

    title:
    更新收货地址标题
    """
    permission_classes = [IsAuthenticated]
    pagination_class = None
    def get_serializer_class(self):
        if self.action == "title":
            return AddressTitleSerializer
        else:
            return AddressSerializer

    def get_queryset(self):
        """获取用户关联的地址查询集"""
        return self.request.user.addresses.filter(is_delete=False)

    # GET /addresses/
    def list(self, request, *args, **kwargs):
        """返回用户地址列表"""
        queryset = self.get_queryset()
        user = self.request.user
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'user_id': user.id,
            'default_address_id': user.default_address_id,
            'limit': constants.USER_ADDRESS_COUNTS_LIMIT,
            'addresses': serializer.data
        })

    # POST /addresses/
    def create(self, request, *args, **kwargs):
        """创建用户地址"""
        # 判断用户地址数量是否超过限制
        count = self.request.user.addresses.filter(is_delete=False).count()
        if count >= constants.USER_ADDRESS_COUNTS_LIMIT:
            return Response({'message': '保存地址数据已达到上限'}, status=status.HTTP_400_BAD_REQUEST)
        # 调用父类方法创建地址
        return super().create(request, *args, **kwargs)

    # delete /addresses/<pk>/
    def destroy(self, request, *args, **kwargs):
        """逻辑删除用户地址"""
        # 获取要删除的地址
        address = self.get_object()
        address.is_delete = True
        address.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # PUT /address/pk/status/
    @action(methods=['put'], detail=True)
    def status(self, request, pk=None):
        """设置默认地址"""
        user = self.request.user
        address = self.get_object()
        # 将地址设置为user的默认收货地址
        user.default_address = address
        user.save()
        return Response({'message': "OK"})

    # PUT /address/pk/title/
    @action(methods=['put'], detail=True)
    def title(self, request, pk=None):
        """修改地址标题"""
        # 获取要修改的地址
        address = self.get_object()
        # 创建序列化器
        serializer = self.get_serializer(instance=address, data=request.data)
        # 验证
        serializer.is_valid(raise_exception=True)
        # 保存
        serializer.save()
        return Response(serializer.data)


class UserHistoryView(CreateModelMixin, GenericAPIView):
    """用户历史浏览记录视图"""
    permission_classes = [IsAuthenticated]
    serializer_class = AddUserHistorySerializer

    def post(self, request):
        """创建用户浏览记录"""
        return self.create(request)

    def get(self, request):
        """获取用户浏览记录"""
        user_id = request.user.id
        history_key = "history_%s" % user_id
        # 查询redis数据库
        redis_conn = get_redis_connection('history')
        sku_ids = redis_conn.lrange(history_key, 0, constants.USER_BROWSING_HISTORY_COUNTS_LIMIT)
        # 根据redis返回的sku_id查询数据库
        # SKU.objects.filter(id__in=sku_ids)  # 这样的结果顺序不对
        sku_list = []
        for sku_id in sku_ids:
            sku_list.append(SKU.objects.get(id=sku_id))
        # 调用序列化器进行序列化
        serializer = SKUSerializer(sku_list, many=True)
        return Response(serializer.data)


class UserAuthorizeView(ObtainJSONWebToken):
    """
    重写用户登录的视图
    因为用户登录是post方法,所以我们覆盖post方法
    """
    def post(self, request, *args, **kwargs):
        # 调用父类的post方法
        response = super().post(request, *args, **kwargs)
        # 判断用户是否可以成功登录,如果登录成功,则获取user对象并执行购物车合并,否则不执行任何操作
        # 获取序列化器
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # 如果能够校验成功,则用户可以登录
            user = serializer.validated_data.get('user')
            response = merge_cart_cookie_to_redis(request, response, user)

        return response
