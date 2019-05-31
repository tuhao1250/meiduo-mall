# 发送短信token的有效期, 单位秒
SEND_SMS_CODE_TOKEN_EXPIRES = 300

# 修改密码的token有效期,单位秒
SET_PASSWORD_TOKEN_EXPIRES = 300

# 验证邮箱token的有效期, 单位秒
VERIFY_EMAIL_TOKEN_EXPIRES = 24 * 3600

# 验证手机号码正则表达式
MOBILE_REGEX = r'^((13[0-9])|(14[5,7])|(15[0-3,5-9])|(17[0,1,3,5-8])|(18[0-9])|166|198|199|(147))\d{8}$'

# 验证邮箱的正则表达式
EMAIL_REGEX = r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$'

# 用户地址数量限制
USER_ADDRESS_COUNTS_LIMIT = 20
