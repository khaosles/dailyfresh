from django.shortcuts import render


# Create your views here.

def index(request):
    '''首页'''
    return render(request, 'index.html')


def detail(request):
    ''' 商品细节'''
    return render(request, 'detail.html')


def list(request):
    ''' 商品列表'''
    return render(request, 'list.html')


