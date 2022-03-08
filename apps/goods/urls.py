from django.urls import path
from apps.goods.views import IndexView
from apps.goods import views

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('detail', views.detail, name='detail'),
    path('list', views.list, name='list'),
]
