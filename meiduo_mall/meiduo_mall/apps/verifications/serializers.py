from rest_framework import serializers
from django_redis import get_redis_connection
from redis.exceptions import RedisError
import logging

logger = logging.getLogger('django')


class CheckImageCodeSerializer(serializers.Serializer):
    """
    图形验证码校验序列化器
    """
    # 校验前端传递的uuid
    image_code_id = serializers.UUIDField(help_text="UUID")
    # 校验用户输入的验证码
    text = serializers.CharField(min_length=4, max_length=4)

    def validate(self, attrs):
        """校验用户输入的图片验证码是否正确,以及60s内是否请求过短信验证码"""
        image_code_id = attrs['image_code_id']
        text = attrs['text']
        # 查询redis数据库,获取真实验证码
        redis_conn = get_redis_connection("verify_codes")
        real_image_code = redis_conn.get("img_%s" % image_code_id)
        # 判断真实验证码是否存在或过期
        if real_image_code is None:
            raise serializers.ValidationError(detail="无效的验证码")

        # 删除redis中的验证码,防止用户对同一个验证码多次请求验证
        try:
            redis_conn.delete('img_%s' % image_code_id)
        except RedisError as result:
            # 如果删除验证码失败,抛出异常,如果不做任何处理,默认会被总的异常处理机制捕获,向前端抛出服务器错误,
            # 但是这里只是为了防止重复验证验证码,不应该返回服务器错误,所以这里需要处理掉,写入日志即可
            logger.error(result)

        # 对比
        real_image_code = real_image_code.decode()  # 转换为字符串
        if real_image_code.lower() != text.lower():
            raise serializers.ValidationError("验证码输入错误")

        # 判断用户在60s内是否请求过短信验证码
        # 如果前端传递过来的还有手机号,则验证手机号是否在60s内请求过验证码,否则只校验验证码即可
        mobile = self.context['view'].kwargs.get('mobile')  # 从当前序列化器对象的context属性中获取手机号
        if mobile:
            # 根据手机号,查询redis数据库判断用户是否在60s内请求过短信验证码
            send_flag = redis_conn.get("send_flag_%s" % mobile)
            if send_flag:
                # 如果有发送过,则校验失败
                raise serializers.ValidationError("发送短信次数过于频繁")
        # 全部校验通过需要返回attrs
        return attrs
