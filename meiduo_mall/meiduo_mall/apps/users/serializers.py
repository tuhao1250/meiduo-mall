from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from django_redis import get_redis_connection
import re
from celery_tasks.emails.tasks import send_verify_mail
from goods.models import SKU
from .models import User, Address
from .utils import get_user_by_account
from . import constants


class CreateUserSerializer(serializers.ModelSerializer):
    """用户模型类序列化器"""
    password2 = serializers.CharField(label="确认密码", help_text="确认密码", write_only=True)  # 确认密码字段,仅在反序列化时使用
    sms_code = serializers.CharField(label="短信验证码", help_text="短信验证码", write_only=True)  # 短信验证码
    allow = serializers.CharField(label="同意协议", help_text="同意协议", write_only=True)  # 同意协议
    token = serializers.CharField(label="认证token", help_text="认证token", read_only=True)  # 返回user对象时包含jwt token

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'password2', 'sms_code', 'mobile', 'allow', 'token']
        extra_kwargs = {
            'id': {"read_only": True},
            'username': {
                "min_length": 5,
                "max_length": 20,
                "error_messages": {
                    'min_length': '用户名仅允许5~20个字符',
                    'max_length': '用户名仅允许5~20个字符'
                }
            },
            'password': {
                'min_length': 8,
                'max_length': 20,
                'write_only': True,  # 仅用于反序列化,返回给前端的时候不能返回密码
                'error_messages': {
                    'min_length': '密码长度为8到20个字符',
                    'max_length': '密码长度为8到20个字符',
                }
            }
        }

    def validate_mobile(self, value):
        """校验手机号"""
        if not re.match(constants.MOBILE_REGEX, value):
            raise serializers.ValidationError("手机格式错误")
        return value

    def validate_allow(self, value):
        """校验是否同意协议"""
        if not value:
            raise serializers.ValidationError("请同意协议")
        return value

    def validate(self, attrs):
        """校验两次密码"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("两次输入的密码不一致")
        # 判断短信验证码
        mobile = attrs['mobile']
        redis_conn = get_redis_connection('verify_codes')
        real_sms_code = redis_conn.get('sms_%s' % mobile)  # 注意从redis中取出的都是bytes类型
        if not real_sms_code:
            # 短信验证码过期
            raise serializers.ValidationError("短信验证码过期,请重新获取")
        if attrs['sms_code'] != real_sms_code.decode():  # 必须确认验证码没有过期才可以加上decode比较,否则会报500错!
            # print(attrs['sms_code'])
            # print("-------")
            # print(real_sms_code)
            # 验证码错误
            raise serializers.ValidationError("短信验证码错误")
        return attrs

    def create(self, validated_data):
        """创建用户"""
        # 移出数据库模型中不存在的属性
        del validated_data['password2']
        del validated_data['allow']
        del validated_data['sms_code']
        # user = super().create(validated_data)
        # # 调用django的认证系统加密密码
        # user.set_password(validated_data['password'])
        # user.save()
        user = User.objects.create_user(**validated_data)
        # 注册成功后,需要让用户处于登录状态
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        user.token = token  # 动态为user对象添加属性
        # print(user.token)
        # print('\n'.join(['%s:%s' % item for item in user.__dict__.items()]))
        return user


class CheckSMSCodeSerializer(serializers.Serializer):
    """检查sms_code的序列化器"""

    sms_code = serializers.CharField(min_length=6, max_length=6, write_only=True)

    def validate_sms_code(self, value):
        """检验sms_code"""
        account = self.context['view'].kwargs['account']
        # 获取user
        user = get_user_by_account(account)
        if not user:
            raise serializers.ValidationError('用户不存在')
        # 把user对象保存到序列化器对象中
        self.user = user
        # 连接redis
        redis_conn = get_redis_connection('verify_codes')
        real_sms_code = redis_conn.get('sms_%s' % user.mobile)
        # 注意可能不存在，可能过期，就算存在取出来的也是字节

        if not real_sms_code:
            # 验证码过期
            raise serializers.ValidationError("短信验证码过期，请重新获取")
        if real_sms_code.decode() != value:
            # 短信验证码错误
            raise serializers.ValidationError('短信验证码错误')

        return value


class ResetPasswordSerializer(serializers.ModelSerializer):
    """重置密码序列化器"""
    password2 = serializers.CharField(label="确认密码", write_only=True)
    access_token = serializers.CharField(label="修改密码凭据", write_only=True)

    class Meta:
        model = User
        fields = ['id', 'password', 'password2', 'access_token']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8~20个字符的密码',
                    'max_length': '仅允许8~20个字符的密码',
                }
            }
        }

    def validate(self, attrs):
        """校验数据"""
        # print("开始校验")
        # 判断两次密码是否输入相等
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("两次输入的密码不一致")
        # 判断access_token
        # print(self.context['view'].kwargs['pk'])
        allow = User.check_set_password_token(attrs['access_token'], self.context['view'].kwargs['pk'])
        if not allow:
            raise serializers.ValidationError("无效的access_token")
        # print("校验成功")
        return attrs

    def update(self, instance, validated_data):
        # 调用django的设置密码的方法
        instance.set_password(validated_data['password'])
        instance.save()
        return instance


class UserDatailSerializer(serializers.ModelSerializer):
    """用户个人信息序列化器"""

    class Meta:
        model = User
        fields = ['id', 'username', 'mobile', 'email', 'email_active']


class EmailSerializer(serializers.ModelSerializer):
    """用户邮箱序列化器"""

    class Meta:
        model = User
        fields = ['id', 'email']
        extra_kwargs = {
            'emial': {
                'required': True,
            }
        }

    def validate_email(self, value):
        if not re.match(constants.EMAIL_REGEX, value):
            raise serializers.ValidationError("无效的邮箱地址")
        return value

    def update(self, instance, validated_data):
        """重写更新方法,保存邮箱,发送激活链接"""
        email = validated_data['email']
        instance.email = email
        instance.save()
        # 发送激活链接
        url = instance.generate_verify_email_url()
        send_verify_mail.delay(instance.username, email, url)
        return instance


class AddressSerializer(serializers.ModelSerializer):
    """用户收货地址序列化器"""
    # 执行反序列化时接收的省市区是id,执行序列化时,需要同时返回id和name
    province_id = serializers.IntegerField(label="省id", required=True)
    city_id = serializers.IntegerField(label="市id", required=True)
    district_id = serializers.IntegerField(label="区id", required=True)
    province = serializers.StringRelatedField(label="省", read_only=True)
    city = serializers.StringRelatedField(label="市", read_only=True)
    district = serializers.StringRelatedField(label="区", read_only=True)

    class Meta:
        model = Address
        exclude = ['user', 'is_delete', 'update_time', 'create_time']

    def validate_mobile(self, value):
        if not re.match(constants.MOBILE_REGEX, value):
            raise serializers.ValidationError("手机号码格式不正确")
        return value

    def create(self, validated_data):
        """创建地址"""
        # print(validated_data)
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class AddressTitleSerializer(serializers.ModelSerializer):
    """用户地址标题序列化器"""
    # 地址标题默认是收货人,可以单独修改,因此需要单的的序列化器

    class Meta:
        model = Address
        fields = ['title']


class AddUserHistorySerializer(serializers.Serializer):
    """用户浏览记录序列化器"""

    sku_id = serializers.IntegerField(min_value=0, label="商品sku编号", help_text="商品sku编号")

    def validate_sku_id(self, value):
        """检验sku_id是否合法"""
        try:
            sku = SKU.objects.get(id=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError("sku_id不存在")
        return value

    def create(self, validated_data):
        """保存用户浏览历史记录"""
        # 获取user_id,sku_id
        user_id = self.context['request'].user.id
        sku_id = validated_data['sku_id']

        # 获取redis连接
        conn = get_redis_connection('history')
        # 创建redis管道
        pl = conn.pipeline()
        history_key = "history_%s" % user_id
        # 去掉已经存在redis中的记录
        # lrem(name, count, value)
        pl.lrem(history_key, 0, sku_id)
        # 从左侧插入本次浏览记录
        # lpush(name, *values)
        pl.lpush(history_key, sku_id)
        # 截断,如果数量超过限制,截取指定区间的数据,丢弃其他数据
        # ltrim(name, start, end)
        pl.ltrim(history_key, 0, constants.USER_BROWSING_HISTORY_COUNTS_LIMIT - 1)
        pl.execute()
        return validated_data

