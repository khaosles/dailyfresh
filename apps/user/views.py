from django.views.generic import View
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.conf import settings
from celery_tasks.tasks import send_register_active_email
from utils.mixin import LoginRequiredMixin
from apps.user.models import Address, User
from apps.goods.models import GoodsSKU
from django_redis import get_redis_connection
import re


# Create your views here.


class RegisterView(View):
    '''注册'''

    def get(self, request):
        '''显示注册页面'''
        return render(request, 'register.html')

    def post(self, request):
        '''注册'''

        # 接收数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')

        # 进行数据校验
        if not all([username, password, email]):
            # 数据不完整
            return render(request, 'register.html', {'errmsg': '数据不完整'})

        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})

        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议'})

        # 判断用户是否存在
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名不存在
            user = None

        if user is not None:
            # 用户名存在
            return render(request, 'register.html', {'errmsg': '用户名已经存在'})

        # 进行业务处理： 进行用户注册
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = 0
        user.save()

        # 发送激活邮件， 包含激活链接
        # 需要包含身份信息，并且加密
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'confirm': user.id}
        token = serializer.dumps(info).decode()

        # celery 发送邮件
        send_register_active_email.delay(email, username, token)

        # 返回应答 跳转到首页
        return redirect(reverse('goods:index'))


class ActiveView(View):
    '''用户激活视图'''

    def get(self, request, token):
        '''进行用户激活'''

        # 进行解密， 获取要激活的用户信息
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            # 解析数据
            info = serializer.loads(token)
            # 获取id
            id = info['confirm']
            # 根据id获取用户信息
            user = User.objects.get(id=id)
            user.is_active = 1
            user.save()

            # 跳转到登录页面
            return redirect(reverse('user:login'))
        except SignatureExpired as err:
            # 激活过期
            return HttpResponse('激活链接已过期')


class LoginView(View):
    '''登录'''

    def get(self, request):
        '''显示登录页面'''

        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''

        return render(request, 'login.html', {'username': username, 'checked': checked})

    def post(self, request):
        '''登录'''

        # 接收数据
        username = request.POST.get('username')
        password = request.POST.get('pwd')

        # 校验
        if not all([username, password]):
            return render(request, 'login.html', {'errmsg': '数据不完整'})

        # 登录校验
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # 获取登录后要跳转的地址
            next_url = request.GET.get('next', reverse('goods:index'))

            # 判断是否需要记住用户名
            remember = request.POST.get('remember')
            # 设置返回的地址
            response = redirect(next_url)
            if remember == 'on':
                # 记住用户名
                response.set_cookie('username', username, max_age=7 * 24 * 3600)
            else:
                response.delete_cookie('username')

            # Redirect to a success page.
            return response
        else:
            return render(request, 'login.html', {'errmsg': '用户名或密码错误'})


class LogoutView(View):
    '''退出登录'''

    def get(self, request):
        '''退出'''
        logout(request)
        # 跳转到首页
        return redirect(reverse('goods:index'))


class CenterInfoView(LoginRequiredMixin, View):

    def get(self, request):
        '''用户信息中心模板类'''

        # 返回true代表用户已经登录
        # request.user.is_authenticated()

        # 获取用户的个人信息
        user = request.user
        address = Address.objects.get_default_addr(user)

        # 获取用户的历史浏览
        # 直接使用redis连接
        # from redis import StrictRedis
        # sr = StrictRedis(host='110.42.145.66', port=6300, db=10, password='gisio123')
        # 连接redis
        conn = get_redis_connection('default')
        # 查询的redis key
        redis_key = 'history_%d' % user.id
        # 查询历史记录
        skuIds = conn.lrange(redis_key, 0, 4)
        goodsList = list()
        # 获取对应的商品信息
        for id in skuIds:
            goodsList.append(GoodsSKU.objects.get(id=id))

        context = {
            'page': 'user',
            'address': address,
            'goodsList': goodsList,
        }

        return render(request, 'user_center_info.html', context)


class CenterOrderView(LoginRequiredMixin, View):

    def get(self, request):
        '''用户中心订单模板类'''

        # 获取用户的订单信息

        return render(request, 'user_center_order.html', {'page': 'order'})


class CenterSiteView(LoginRequiredMixin, View):

    def get(self, request):
        '''收货地址模板类'''

        # 获取用户的个人收货地址
        # 获取当前用户对象
        user = request.user
        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     # 不存在默认收货地址
        #     address = None
        address = Address.objects.get_default_addr(user)

        return render(request, 'user_center_site.html', {'page': 'address', 'address': address})

    def post(self, request):
        '''提交收货地址'''
        # 接收数据
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')

        # 校验数据
        if not all([receiver, addr, phone]):
            return render(request, 'user_center_site.html', {'errmsg': '数据不完整'})
        # 校验手机号
        if not re.match('1\d{10}', phone):
            return render(request, 'user_center_site.html', {'errmsg': '手机号输入有误'})

        # 地址添加
        # 获取当前用户对象
        user = request.user
        address = Address.objects.get_default_addr(user)

        if address:
            is_default = False
        else:
            is_default = True

        Address.objects.create(user=user,
                               addr=addr,
                               zip_code=zip_code,
                               recevier=receiver,
                               phone=phone,
                               is_default=is_default)
        # 返回应答
        return redirect(reverse('user:address'))




