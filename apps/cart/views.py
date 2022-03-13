from django.shortcuts import render
from django.views.generic import View
from django.http.response import JsonResponse
from apps.goods.models import GoodsSKU
from django_redis import get_redis_connection
from utils.mixin import LoginRequiredMixin


# Create your views here.


class CartView(LoginRequiredMixin, View):

    def get(self, request):
        '''购物车'''
        # 用户
        user = request.user
        # 获取用户购物车商品的信息
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        cart_dict = conn.hgetall(cart_key)

        skus = list()
        # 总数目
        total_count = 0
        # 总价格
        total_amount = 0
        # 商品信息
        for sku_id, count in cart_dict.items():
            # 根据id获取信息
            sku = GoodsSKU.objects.get(id=sku_id)
            amount = sku.price * int(count)
            # 小记
            sku.amount = amount
            # 数量
            sku.count = int(count)

            total_amount += amount
            total_count += int(count)
            # 添加
            skus.append(sku)

        context = {
            'total_count': total_count,
            'total_amount': total_amount,
            'skus': skus,
        }

        return render(request, 'cart.html', context)


class CartAddView(View):
    '''添加购物车'''

    def post(self, request):
        '''购物车记录添加'''
        # 接收数据
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')
        user = request.user

        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})

        # 数据校验
        if not all([sku_id, count]):
            return JsonResponse({'res': 1, 'errmsg': '数据不完整'})

        # 检验商品数量
        try:
            count = int(count)
            # if count <= 0:
            #     raise Exception('商品数量不能必须大于0')
        except Exception as e:
            return JsonResponse({'res': 2, 'errmsg': '商品数量出错'})

        # 检验商品是否存在
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'res': 3, 'errmsg': '商品不存在'})

        # 业务处理 ；添加购物车
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        # 不存在，返回none
        cart_count = conn.hget(cart_key, sku_id)
        if cart_count:
            count += int(cart_count)
        # 校验商品的库存
        if count > sku.stock:
            return JsonResponse({'res': 4, 'errmsg': '商品库存不足'})

        # 设置key对应的值
        conn.hset(cart_key, sku_id, count)

        # 计算用户购物车中商品到条目
        total_count = conn.hlen(cart_key)

        # 返回应答
        return JsonResponse({'res': 5, 'msg': '添加成功', 'total_count': total_count})
