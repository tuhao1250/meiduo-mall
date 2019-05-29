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
    email_active = models.BooleanField(default=False, verbose_name="邮箱验证状态", help_text="邮箱验证状态")

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
            'user_id': self.id
        }
        token = serializer.dumps(data)
        return token.decode()

    @staticmethod
    def check_set_password_token(token, user_id):
        """检验设置密码的token"""
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=constants.SET_PASSWORD_TOKEN_EXPIRES)
        try:
            data = serializer.loads(token)
            print(data)
        except BadData:
            return False
        else:
            return user_id == data.get('user_id')

    def generate_verify_email_url(self):
        """
        生成激活邮件URL地址
        :return: verify_url 激活链接地址
        """
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=constants.VERIFY_EMAIL_TOKEN_EXPIRES)
        data = {
            "user_id": self.id,
            "email": self.email
        }
        token = serializer.dumps(data).decode()
        verify_url = "http://www.meiduo.site:8080/success_verify_email.html?token=" + token
        return verify_url

    @staticmethod
    def check_verify_email_token(token):
        """
        检验激活邮箱的token
        :param token: 需要检验的token
        :return:
        """
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=constants.VERIFY_EMAIL_TOKEN_EXPIRES)
        try:
            data = serializer.loads(token)
        except BadData:
            return False
        user_id = data.get('user_id')
        email = data.get('email')
        user = User.objects.filter(id=user_id, email=email).update(email_active=True)
        return user



