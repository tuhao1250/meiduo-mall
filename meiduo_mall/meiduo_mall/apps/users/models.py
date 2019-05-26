from django.db import models
from django.contrib.auth.models import AbstractUser
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer
from itsdangerous import BadData
from django.conf import settings
from . import constants
# Create your models here.


class User(AbstractUser):
    """用户模型类"""

    mobile = models.CharField(max_length=11, unique=True, verbose_name="手机号", help_text="手机号")

    class Meta:
        db_table = 'tb_users'
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    def generic_send_sms_code_token(self):
        """
        生成发送短信验证码的access_token
        :return: access_token
        """
        # 创建itsdangerous的转换工具
        serializer = TJWSSerializer(settings.SECRET_KEY, constants.SEND_SMS_CODE_TOKEN_EXPIRES)
        # 创建需要加密转换的数据
        data = {
            'mobile': self.mobile
        }
        token_bytes = serializer.dumps(data)
        return token_bytes.decode()

    @staticmethod
    def check_send_sms_code_token(token):
        """
        校验access_token
        :return: mobile or None
        """
        # 创建itsdangerous的转换工具
        serializer = TJWSSerializer(settings.SECRET_KEY, constants.SEND_SMS_CODE_TOKEN_EXPIRES)
        try:
            data = serializer.loads(token)
        except BadData:
            return None
        else:
            mobile = data.get('mobile')
            return mobile

    def generate_set_password_token(self):
        """生成修改密码的token"""
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=constants.SET_PASSWORD_TOKEN_EXPIRES)
        data = {
            'user_id': self.pk
        }
        token = serializer.dumps(data)
        return token.decode()