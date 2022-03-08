from django.urls import path
from apps.order.views import PlaceOrderView

urlpatterns = [
    path('place_order', PlaceOrderView.as_view(), name='place_order'),  # 提交订单

]
