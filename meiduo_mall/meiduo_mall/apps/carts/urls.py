from django.urls import path
from . import views


app_name = "carts"


urlpatterns = [
    path('cart/', views.CartView.as_view()),  # 购物车接口
    path('cart/selection/', views.CartSelectAllView.as_view()),  # 购物车全选接口
]