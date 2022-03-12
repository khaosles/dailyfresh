from django.shortcuts import render, redirect, reverse
from django.views.generic import View
from django.core.cache import cache
from django.core.paginator import Paginator
from apps.goods.models import GoodsType, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner, GoodsSKU
from apps.order.models import OrderGoods
from django_redis import get_redis_connection


# Create your views here.


class IndexView(View):
    '''首页'''

    def get(self, request):
        '''显示首页'''

        # 获取缓存
        context = cache.get('index_page_data')

        # 如果不存在缓存， 则读取数据
        if context is None:

            # 获取商品种类信息
            types = GoodsType.objects.all()
            # 获取首页轮播商品信息
            goods_banners = IndexGoodsBanner.objects.all().order_by('index')
            # 获取首页促销活动信息
            promotion_banners = IndexPromotionBanner.objects.all().order_by('index')

            # 获取分类商品展示信息
            for type in types:
                # 获取type种类首页分类商品的图片展示信息
                image_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by('index')
                # 获取type种类首页分类商品的文字展示信息
                title_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by('index')

                # 动态给type增加属性，分别保存首页分类商品的图片展示信息和文字展示信息
                type.image_banners = image_banners
                type.title_banners = title_banners

            # 组织模板上下文
            context = {'types': types,
                       'goods_banners': goods_banners,
                       'promotion_banners': promotion_banners, }
            # 设置缓存
            cache.set('index_page_data', context, 3600)

        # 获取用户购物车中商品的数目
        user = request.user
        # 购物车默认数量为 0
        cart_count = 0
        if user.is_authenticated:
            # 用户已登录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)

        # 组织模板上下文
        context.update(cart_count=cart_count)
        # 使用模板
        return render(request, 'index.html', context)


# /goods/id
class DetailView(View):
    '''详情页视图'''

    def get(self, request, goods_id):
        ''' 商品细节'''

        try:
            sku = GoodsSKU.objects.get(id=goods_id)
        except GoodsSKU.DoesNotExist:
            return redirect(reverse('goods:index'))

        # 商品类型
        types = GoodsType.objects.all()
        # 新品推荐
        new_skus = GoodsSKU.objects.filter(type=sku.type).exclude(id=sku.id).order_by('-create_time')[:2]
        # 评论
        orders = OrderGoods.objects.filter(sku=sku).exclude(comment='')

        # 获取与该商品同一spu的其他规格的商品
        same_spu_skus = GoodsSKU.objects.filter(goods=sku.goods).exclude(id=sku.id)

        # 获取用户购物车中商品的数目
        user = request.user
        # 购物车默认数量为 0
        cart_count = 0
        if user.is_authenticated:
            # 用户已登录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)

            # 添加历史浏览记录
            conn = get_redis_connection('default')
            history = 'history_%s' % request.user.id
            # 删除存在记录
            conn.lrem(history, 0, goods_id)
            # 添加新的浏览记录
            conn.lpush(history, goods_id)
            # 保留最新的五条浏览记录
            conn.ltrim(history, 0, 4)

        context = {
            'sku': sku,
            'types': types,
            'cart_count': cart_count,
            'orders': orders,
            'new_skus': new_skus,
            'same_spu_skus': same_spu_skus,
        }

        return render(request, 'detail.html', context)


class ListView(View):

    def get(self, request, type_id, page):
        ''' 商品列表'''

        # 查询类型
        try:
            type = GoodsType.objects.get(id=type_id)
        except GoodsType.DoesNotExist:
            return redirect(reverse('goods:index'))

        # 获取种类信息
        types = GoodsType.objects.all()

        sort = request.GET.get('sort')
        # 按照人气排序查询该类的sku
        if sort == 'sales':
            skus = GoodsSKU.objects.filter(type=type).order_by('-sales')
        # 按照价格方式查询该类的sku
        elif sort == 'price':
            skus = GoodsSKU.objects.filter(type=type).order_by('-price')
        # 默认方式查询该类型的sku
        else:
            sort = 'default'
            skus = GoodsSKU.objects.filter(type=type).order_by('-create_time')

        # 商品分页
        paginator = Paginator(skus, 1)

        # 读取page页数据
        try:
            page = int(page)
        except Exception as e:
            page = 1
        if page > paginator.num_pages:
            page = 1
        skus_page = paginator.page(page)

        num_pages = paginator.num_pages
        # 每页最多显示五个页码
        # 如果不足五个，则全部显示
        if num_pages < 5:
            pages = range(1, num_pages + 1)
        # 如果当前页码为前三页，显示12345
        elif page <= 3:
            pages = range(1, 6)
        # 如果当前页为后三页，显示-12345
        elif num_pages - page < 2:
            pages = range(num_pages - 4, num_pages + 1)
        # 显示当前页前两页，当前页，后两页
        else:
            pages = range(page - 2, page + 3)
        # 新品信息
        new_skus = GoodsSKU.objects.filter(type=type).order_by('-create_time')[:2]

        # 购物车数量
        cart_count = 0
        if request.user.is_authenticated:
            cart_key = 'cart_%s' % request.user.id
            conn = get_redis_connection('default')
            cart_count = conn.hlen(cart_key)

        context = {
            'type': type,
            'types': types,
            'skus_page': skus_page,
            'new_skus': new_skus,
            'cart_count': cart_count,
            'sort': sort,
            'pages': pages
        }

        return render(request, 'list.html', context)
