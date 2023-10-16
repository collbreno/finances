import json

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from ..models import User, Tunnel
from ..utils import get_stock_data


def tunnel_form_page(request, stock_symbol):
    stock_data = get_stock_data(stock_symbol)
    emails = list(map(lambda p: p.email, User.objects.all()))    

    context = {
        'emails': emails,
        'graph_data': json.dumps(stock_data['graph_data']),
        'date': stock_data['date'],
        'stock_symbol': stock_symbol.upper(),
    }

    return render(request, 'finances/tunnel_form.html', context)

def delete_tunnel(request):
    tunnel_id = request.POST['tunnel_id']
    tunnel = Tunnel.objects.get(pk=tunnel_id)
    tunnel.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def add_tunnel(request):
    email = request.POST['email']
    user = User.objects.get(email=email)
    stock_symbol = request.POST['stock_symbol']
    min_limit = request.POST['min_limit']
    max_limit = request.POST['max_limit']
    time_interval = request.POST['time_interval']
    tunnel = Tunnel(
        user=user, 
        stock_symbol=stock_symbol.upper(), 
        min_limit=min_limit, 
        max_limit=max_limit,
        time_interval=time_interval,
    )
    tunnel.save()
    return HttpResponseRedirect(reverse("finances:stock", args=(stock_symbol,)))
