from django.urls import path, re_path
from django.contrib.auth.decorators import login_required
from apps.user.views import RegisterView, ActiveView, LoginView, CenterInfoView, CenterOrderView, CenterSiteView, LogoutView

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),  # 用户注册
    re_path('^active/(?P<token>.*)$', ActiveView.as_view(), name='active'),  # 用户激活
    path('login', LoginView.as_view(), name='login'),  # 登录
    path('logout', LogoutView.as_view(), name='logout'),  # 退出
    path('',  CenterInfoView.as_view(), name='user'),  # 用户信息中心
    path('order', CenterOrderView.as_view(), name='order'),  # 用户中心订单
    path('address', CenterSiteView.as_view(), name='address'),  # 用户中心订单

]

