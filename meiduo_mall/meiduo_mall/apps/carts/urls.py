from django.urls import path
from . import views


app_name = "carts"


urlpatterns = [
    path('cart/', views.CartView.as_view()),  # 购物车接口
]