from django.conf import settings
from urllib.parse import urlencode, parse_qs
from urllib.request import urlopen
import logging
import json
from .exceptions import QQAPIException

logger = logging.getLogger('django')


class OAuthQQ(object):
    """
    用于QQ登录的工具类,提供QQ登录可能使用的方法
    """
    def __init__(self, app_id=None, app_key=None, redirect_uri=None, state=None):
        self.app_id = app_id or settings.QQ_APP_ID
        self.app_key = app_key or settings.QQ_APP_KEY
        self.redirect_uri = redirect_uri or settings.QQ_REDIRECT_URI
        self.state = state or settings.QQ_STATE

    def generate_qq_login_url(self):
        """
        拼接用户QQ登录的url地址
        :return: url地址
        """
        url = "https://graph.qq.com/oauth2.0/authorize?"
        data = {
            "response_type": "code",
            "client_id": self.app_id,
            "redirect_uri": self.redirect_uri,
            "state": self.state,
            "scope": 'get_user_info',  # 仅获取用户QQ的open_id
        }
        # 将python字典转换为查询字符串
        query_string = urlencode(data)  # xxx=xxx&xxx=xxx&...
        url += query_string
        # print(url)
        return url

    def get_access_token(self, code):
        """
        获取qq的access_token
        :param code: 调用的凭据
        :return: access_token
        """
        url = "https://graph.qq.com/oauth2.0/token?"
        request_data = {
            "grant_type": "authorization_code",
            "client_id": self.app_id,
            "client_secret": self.app_key,
            "code": code,
            "redirect_uri": self.redirect_uri
        }
        url += urlencode(request_data)

        try:
            # 使用python标准模块urllib发送请求
            response = urlopen(url)
            # 读取qq服务器返回的响应体数据
            response = response.read().decode()  # 注意将字节转换为字符串
            # access_token=FE04************************CCE2&expires_in=7776000&refresh_token=88E4************************BE14
            # 将qq返回的数据转换为python的字典
            resp_dict = parse_qs(response)
            access_token = resp_dict.get('access_token')[0]
            # print(access_token)
        except Exception as e:
            logger.error(e)
            # 需要抛出异常
            raise QQAPIException("获取QQ的access_token异常")

        return access_token

    def get_open_id(self, access_token):
        """
        获取QQ用户的open_id
        :param access_token: 上一步获取到的QQ提供的access_token
        :return: QQ用户的open_id
        """
        # 获取url
        url = "https://graph.qq.com/oauth2.0/me?access_token=" + access_token
        print(url)
        try:
            # 发送请求
            response = urlopen(url)
        except Exception as e:
            logger.error(e)
            raise QQAPIException("发送请求openid出现异常")
        # 读取响应数据
        resp_data = response.read().decode()
        # QQ返回的数据:callback( {"client_id":"YOUR_APPID","openid":"YOUR_OPENID"} )\n;
        # 从QQ返回的数据中解析出字典
        # print(resp_data)
        try:
            resp_dict = json.loads(resp_data.split(" ")[1])
        except Exception as e:
            # 出现异常说明接口调用有错误时，会返回code和msg字段，以url参数对的形式返回，value部分会进行url编码（UTF-8）
            resp_dict = parse_qs(resp_data)
            logger.error('code=%s msg=%s' % (resp_dict.get('code')[0], resp_dict.get('msg')[0]))
            raise QQAPIException("QQ接口调用出现异常")
        # 获取openid
        openid = resp_dict.get('openid')
        return openid















