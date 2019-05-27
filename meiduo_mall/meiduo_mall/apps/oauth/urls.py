from django.urls import path
from . import views


app_name = "oauth"

urlpatterns = [
    path('qq/authorization/', views.OAuthQQURLView.as_view()),  # 获取QQ第三方登录的url
    path('qq/user/', views.OAuthQQUserView.as_view()),  # 获取QQ第三方登录的用户
]