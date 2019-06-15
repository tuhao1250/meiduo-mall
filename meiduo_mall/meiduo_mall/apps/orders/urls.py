from django.urls import path
from . import views

app_name = "orders"


urlpatterns = [
    path('orders/settlement/', views.OrderSettlementView.as_view()),  # 订单结算页面视图
    path('orders/', views.SaveOrderView.as_view()),  # 保存订单视图
    path('orders/all/', views.OrdersAllView.as_view()),  # 获取所有订单信息
]