from django.contrib import admin
from apps.goods.models import *
from django.core.cache import cache
from celery_tasks.tasks import generate_static_html
# Register your models here.

class BaseAmdin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        '''重写保存模型方法'''

        # 保存模型
        super().save_model(request, obj, form, change)
        # 重新生成静态页面
        generate_static_html.delay()

        # 清除首页缓存数据
        cache.delete('index_page_data')


    def delete_model(self, request, obj):
        '''重写删除模型方法'''

        # 删除数据
        super().delete_model(request, obj)
        # 重新生成静态页面
        generate_static_html.delay()

        # 清除首页缓存数据
        cache.delete('index_page_data')


class IndexPromotionBannerAdmin(BaseAmdin):
    pass

class IndexTypeGoodsBannerAdmin(BaseAmdin):
    pass

class IndexGoodsBannerAdmin(BaseAmdin):
    pass

class GoodsTypeAdmin(BaseAmdin):
    pass


admin.site.register(GoodsSKU)
admin.site.register(Goods)
admin.site.register(GoodsImage)
admin.site.register(GoodsType, GoodsTypeAdmin)
admin.site.register(IndexGoodsBanner, IndexGoodsBannerAdmin)
admin.site.register(IndexTypeGoodsBanner, IndexTypeGoodsBannerAdmin)
admin.site.register(IndexPromotionBanner, IndexPromotionBannerAdmin)