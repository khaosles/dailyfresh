from django.urls import path
from apps.cart.views import CartView


urlpatterns = [
    path('', CartView.as_view(), name='cart'),  # 购物车

]
