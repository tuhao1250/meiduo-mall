from rest_framework import serializers
from django_redis import get_redis_connection
from users.models import User
from .models import OAuthQQUser


class OAuthQQUserSerializer(serializers.ModelSerializer):
    """
    保存QQ用户序列化器
    """
    sms_code = serializers.CharField(label="短信验证码", help_text="短信验证码", min_length=6, max_length=6, write_only=True)
    access_token = serializers.CharField(label="操作凭证", help_text="操作凭证", write_only=True)
    token = serializers.CharField(label="登录token", help_text="登录token", read_only=True)
    mobile = serializers.RegexField(label="手机号", help_text="手机号",
                    regex=r'((13[0-9])|(14[5,7])|(15[0-3,5-9])|(17[0,1,3,5-8])|(18[0-9])|166|198|199|(147))\d{8}')

    class Meta:
        model = User
        fields = ['id', 'username', 'token', 'sms_code', 'access_token', 'mobile', 'password']
        extra_kwargs = {
            'id': {
                'read_only': True
            },
            'username': {
                'read_only': True
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            },

        }

    def validate(self, attrs):
        """
        校验函数
        :param attrs:
        :return:
        """
        # 检验access_token
        access_token = attrs['access_token']
        openid = OAuthQQUser.check_save_user_token(access_token)
        if not openid:
            raise serializers.ValidationError("无效的access_token")
        attrs['openid'] = openid

        # 检验短信验证码
        mobile = attrs['mobile']
        sms_code = attrs['sms_code']
        redis_conn = get_redis_connection('verify_codes')
        real_sms_code = redis_conn.get('sms_%s' % mobile)
        if real_sms_code.decode() != sms_code:
            raise serializers.ValidationError('短信验证码错误')

        # 检验用户是否存在
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 用户不存在
            pass
        else:
            # 用户已存在,需要校验密码
            password = attrs['password']
            if not user.check_password(password):
                raise serializers.ValidationError("密码错误")
            # 校验成功保存uesr
            attrs['user'] = user
        return attrs

    def create(self, validated_data):
        # 获取openid
        openid = validated_data['openid']
        mobile = validated_data['mobile']
        password = validated_data['password']

        # 尝试获取user
        user = validated_data.get('user')
        if not user:
            # 用户不存在,先创建用户
            user = User.objects.create_user(username=mobile, mobile=mobile, password=password)
        # 用户存在,创建QQ用户与美多用户的绑定关系
        OAuthQQUser.objects.create(user=user, openid=openid)
        return user
