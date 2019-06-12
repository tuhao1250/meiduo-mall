"""meiduo_mall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('oauth/', include('oauth.urls', namespace="oauth")),  # 包含oauth模块的urls
    path('', include('users.urls', namespace="users")),  # 包含用户模块urls
    path('', include('verifications.urls', namespace="verifications")),  # 包含验证码模块的urls
    path('', include('areas.urls', namespace="areas")),  # 包含areas模块的urls
    path('ckeditor/', include('ckeditor_uploader.urls')),  # 包含ckeditor的url
    path('', include('goods.urls', namespace="goods")),  # 包含商品模块的urls
    path('', include('carts.urls', namespace="carts")),  # 包含购物车模块的urls
    path('orders/', include('orders.urls', namespace="orders")),  # 包含订单模块的urls
]
