from django.urls import path
from . import views
from users.converters import MobileConverter

# register_converter(MobileConverter, "mobile")

app_name = "verifications"

urlpatterns = [
    path('image_codes/<str:image_code_id>/', views.ImageCodeView.as_view(), name="verify_code"),  # 获取图片验证码
    path(r'sms_codes/<mobile:mobile>/', views.SMSCodeView.as_view(), name="sms_code"),  # 获取短信验证码
    path(r'sms_codes/', views.SMSCodeByTokenView.as_view()),  # 找回密码根据access_token获取短信验证码
]