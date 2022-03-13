from django.urls import path
from apps.cart.views import CartView, CartAddView


urlpatterns = [
    path('add', CartAddView.as_view(), name='add'), # 添加数据到购物车
    path('', CartView.as_view(), name='cart'),  # 购物车

]
