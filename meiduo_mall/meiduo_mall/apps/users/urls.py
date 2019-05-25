from django.urls import path, register_converter
from rest_framework_jwt.views import obtain_jwt_token
from . import views, converters

app_name = "users"

register_converter(converters.UsernameConverter, 'username')
register_converter(converters.MobileConverter, 'mobile')

urlpatterns = [
    path('usernames/<username:username>/count/', views.UsernameCountView.as_view(), name="count_username"),  # 查询用户名数量
    path('mobiles/<mobile:mobile>/count/', views.MobileCountView.as_view(), name="count_mobile"),  # 查询手机号对应用户名数量
    path('users/', views.UserView.as_view(), name="register"),  # 注册接口
    path('authorizations/', obtain_jwt_token),  # 登录接口
]