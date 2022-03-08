from django.urls import path
from apps.goods import views

urlpatterns = [
    path('', views.index, name='index'),
    path('detail', views.detail, name='detail'),
    path('list', views.list, name='list'),
]
