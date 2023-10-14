import json
import locale

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import generic

from .models import User, Tunnel, Notification
from .utils import get_stock_graph_data

def index(request):
    return render(request, "finances/index.html")

def symbols(request):
    context = {
        'symbols': ['GOGL34.SA', 'AAPL34.SA', 'ABEV3.SA', 'U1BE34.SA', 'NFLX34.SA'],
    }
    return render(request, "finances/symbols.html", context=context)

def new_user_form(request):
    return render(request, "finances/new_user_form.html")

def add_user(request):
    name = request.POST["name"]
    email = request.POST["email"]
    user = User(name=name, email=email)
    user.save()
    return HttpResponseRedirect(reverse("finances:users"))

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
    return HttpResponseRedirect(reverse("finances:symbol", args=(stock_symbol,)))

def delete_tunnel(request):
    tunnel_id = request.POST['tunnel_id']
    tunnel = Tunnel.objects.get(pk=tunnel_id)
    tunnel.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class UsersView(generic.ListView):
    model = User
    template_name = "finances/users.html"
    context_object_name = "users"

class UserView(generic.DetailView):
    model = User
    template_name = "finances/user.html"
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tunnels = self.get_object().tunnel_set.all()
        context["tunnels"] = tunnels

        context["notifications"] = Notification.objects.filter(tunnel__user=self.get_object())
        return context
    

def tunnel_form(request, stock_symbol):
    graph_data = get_stock_graph_data(stock_symbol)
    emails = list(map(lambda p: p.email, User.objects.all()))    

    context = {
        'emails': emails,
        'graph_data': json.dumps(graph_data),
        'stock_symbol': stock_symbol.upper(),
    }

    return render(request, 'finances/tunnel_form.html', context)

def symbol(request, stock_symbol):
    graph_data = get_stock_graph_data(stock_symbol)
    tunnels = Tunnel.objects.filter(stock_symbol=stock_symbol)
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

    context = {
        'graph_data': json.dumps(graph_data),
        'stock_symbol': stock_symbol.upper(),
        'tunnels': tunnels,
        'last_price': locale.currency(graph_data['y'][-1]),
        'last_datetime': graph_data['x'][-1],
    }

    return render(request, 'finances/symbol.html', context)