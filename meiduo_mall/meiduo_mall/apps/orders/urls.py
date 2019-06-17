from django.urls import path
from . import views

app_name = "orders"


urlpatterns = [
    path('orders/settlement/', views.OrderSettlementView.as_view()),  # 订单结算页面视图
    path('orders/', views.SaveOrderView.as_view()),  # 保存订单视图
    path('orders/all/', views.OrdersAllView.as_view()),  #
    path('orders/<str:order_id>/uncommentgoods/', views.UncommentGoodsView.as_view()),  # 获取未评论商品列表
    path('skus/<int:sku_id>/comments/', views.SKUCommentView.as_view()),  # 订单评论
]
