from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views


app_name = 'goods'

urlpatterns = [
    path(r'categories/<int:category_id>/hotskus/', views.HotSKUListView.as_view()),  # 返回商品SKU热销数据
    path(r'categories/<int:category_id>/skus/', views.SKUListView.as_view()),  # 获取商品列表
    path(r'categories/<int:cat_id>/', views.CatView.as_view()),  # 获取商品分类面包屑导航
]

router = DefaultRouter()
router.register('skus/search', views.SKUSearchViewSet, base_name='skus_search')

urlpatterns += router.urls