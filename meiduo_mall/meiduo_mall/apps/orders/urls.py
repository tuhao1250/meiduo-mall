from django.urls import path
from . import views

app_name = "orders"


urlpatterns = [
    path('settlement/', views.OrderSettlementView.as_view()),  # 订单结算页面视图
    path('', views.SaveOrderView.as_view()),  # 保存订单视图
]