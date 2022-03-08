#!usr/bin/env python
# -*- coding: utf-8 -*-

'''
    @author: khaosles
    @date: 2022/3/1  17:01
'''

from celery import Celery
from django.conf import settings
from django.core.mail import send_mail

# 在任务处理者端添加代码, django环境的初始化
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dailyfresh.settings')
django.setup()

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



