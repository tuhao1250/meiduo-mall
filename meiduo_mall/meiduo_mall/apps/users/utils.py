from django.contrib.auth.backends import ModelBackend
import re
from .models import User


def jwt_response_payload_handler(token, user=None, request=None):
    """
    自定义jwt认证成功返回数据
    """
    return {
        'token': token,
        'user_id': user.id,
        'username': user.username
    }


def get_user_by_account(account):
    """
    根据账号信息查询用户对象
    :param account: 可以是手机号也可以是用户名
    :return: 存在返回User对象,否则返回None
    """
    try:
        # 判断account是否是手机号
        if re.match(r'((13[0-9])|(14[5,7])|(15[0-3,5-9])|(17[0,1,3,5-8])|(18[0-9])|166|198|199|(147))\d{8}', account):
            # 根据手机号查询
            user = User.objects.get(mobile=account)
        else:
            # 根据用户名查询
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        return user


class UsernameMobileAuthBackend(ModelBackend):
    """自定义的认证方法后端"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        自定义的认证方法
        :param request: 本次请求的对象
        :param username: 用户账号,可能是用户名也可能是手机号
        :param password: 前端传递的密码
        :param kwargs: 额外的参数
        :return:
        """
        # 根据username查询出用户对象
        user = get_user_by_account(username)
        # 如果用户对象存在,再调用user对象的check_password方法校验密码
        if user and user.check_password(password):
            # 验证成功,返回用户对象
            return user
