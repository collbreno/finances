import yfinance as yf
import json
import locale

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from requests.exceptions import HTTPError
from django.urls import reverse
from django.views import generic

from .models import User, Tunnel

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

def add_user_stock(request):
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
    return HttpResponseRedirect(reverse('finances:users'))

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
        context["tunnels"] = self.get_object().tunnel_set.all()
        return context
    

def tunnel_form(request, stock_symbol):
    df = yf.download(stock_symbol, period='1day', interval='1m')
    emails = list(map(lambda p: p.email, User.objects.all()))    
    graph_data = {
        'x': df.index.strftime('%H:%M').tolist(),
        'y': df['Close'].tolist(),
    }

    context = {
        'emails': emails,
        'graph_data': json.dumps(graph_data),
        'stock_symbol': stock_symbol.upper(),
    }

    return render(request, 'finances/tunnel_form.html', context)

def symbol(request, stock_symbol):
    df = yf.download(stock_symbol, period='1day', interval='1m')
    tunnels = Tunnel.objects.filter(stock_symbol=stock_symbol)
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    last_price = locale.currency(df['Close'].iloc[-1])

    graph_data = {
        'x': df.index.strftime('%H:%M').tolist(),
        'y': df['Close'].tolist(),
    }

    context = {
        'graph_data': json.dumps(graph_data),
        'stock_symbol': stock_symbol.upper(),
        'tunnels': tunnels,
        'last_price': last_price,
    }

    return render(request, 'finances/symbol.html', context)