from django.shortcuts import render
from django.views.generic import View
# Create your views here.


class PlaceOrderView(View):

    def get(self, request):
        '''提交订单'''
        return render(request, 'place_order.html')
