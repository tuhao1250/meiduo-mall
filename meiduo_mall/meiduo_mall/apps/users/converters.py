class UsernameConverter(object):
    """用户名转换器"""
    regex = '\w{5,20}'

    def to_python(self, value):
        """从url中匹配结果转换成python变量"""
        return value

    def to_url(self, value):
        """从python变量转换为url"""
        return value


class MobileConverter(object):
    """手机号码转换器"""
    regex = r'((13[0-9])|(14[5,7])|(15[0-3,5-9])|(17[0,1,3,5-8])|(18[0-9])|166|198|199|(147))\d{8}'

    def to_python(self, value):
        """从url中提取手机号转换成python字符串"""
        return str(value)

    def to_url(self, value):
        """从python字符串转换为url中的内容"""
        return value