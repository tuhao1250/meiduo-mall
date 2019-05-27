from django.db import models
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer
from itsdangerous import BadData

from meiduo_mall.utils.models import BaseModel
from . import constants

# Create your models here.


class OAuthQQUser(BaseModel):
    """
    QQ登录用户数据
    """
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='用户')
    openid = models.CharField(max_length=64, verbose_name='openid', db_index=True)

    class Meta:
        db_table = 'tb_oauth_qq'
        verbose_name = 'QQ登录用户数据'
        verbose_name_plural = verbose_name

    @staticmethod
    def generate_save_user_token(openid):
        """
        根据qq返回的openid生成保存用户数据的token
        :param openid: 调用QQAPI得到的QQ用户的openid
        :return: token
        """
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=constants.SAVE_QQ_USER_TOKEN_EXPIRES)
        data = {
            "openid": openid
        }
        token = serializer.dumps(data)
        return token.decode()

    @staticmethod
    def check_save_user_token(access_token):
        """
        根据传入的access_token,解析出open_id,并返回
        :param access_token:
        :return:
        """
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=constants.SAVE_QQ_USER_TOKEN_EXPIRES)
        try:
            data = serializer.loads(access_token)
        except BadData:
            return None
        return data.get('openid')
