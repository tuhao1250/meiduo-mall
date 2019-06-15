from django.urls import path
from . import views


app_name = "payment"

urlpatterns = [
    path('orders/<str:order_id>/payment/', views.AlipayView.as_view()),  # 获取支付宝支付链接
    path('payment/status/', views.SavePaymentView.as_view()),  # 保存支付宝支付结果视图
]