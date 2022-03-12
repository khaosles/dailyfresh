#!usr/bin/env python
# -*- coding: utf-8 -*-

'''
    @author: khaosles
    @date: 2022/3/1  17:01
'''

from celery import Celery
from django.conf import settings
from django.core.mail import send_mail
from django.template import loader, RequestContext

# # 在任务处理者端添加代码, django环境的初始化
# import os
# import django
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dailyfresh.settings')
# django.setup()
# from apps.goods.models import GoodsType, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner



# 创建一个Celery对象
app = Celery('celery_tasks.tasks', broker='redis://:gisio123@110.42.145.66:6300/8')


@app.task
def send_register_active_email(to_mail, username, token):
    '''发送激活邮件'''

    subject = '天天生鲜欢迎信息'
    html_message = '<meta http-equiv="Content-Type" content="text/html;charset=UTF-8"><h1>%s  欢迎您成为天天生鲜会员</h1>请点击以下链接激活:<br/><a href="http:127.0.0.1:8000/user/active/%s">http:127.0.0.1:8000/user/active/%s</a>' % (
        username, token, token
    )
    message = ''
    sender = settings.EMAIL_FROM
    recipient_list = [
        to_mail,
    ]
    # 发邮件
    send_mail(subject=subject, message=message, html_message=html_message,
              from_email=sender, recipient_list=recipient_list)

@app.task
def generate_static_html():
    '''产生静态页面'''
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
               'promotion_banners': promotion_banners,}

    # 加载模版文件
    template = loader.get_template('index_static.html')
    # 定义模版上下文， 可以省略
    # context = RequestContext(request, context)
    # 模版渲染
    static_index_html = template.render(context)

    # 生成首页对应静态文件
    save_path = os.path.join(settings.BASE_DIR, 'static', 'index.html')
    with open(save_path, 'w') as fp:
        fp.write(static_index_html)