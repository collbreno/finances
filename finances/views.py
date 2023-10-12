import yfinance as yf
import json

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from requests.exceptions import HTTPError
from django.urls import reverse
from django.views import generic

from .models import Person, PersonStock

def index(request):
    return render(request, "finances/index.html")

def symbols(request):
    context = {
        'symbols': ['GOGL34.SA', 'AAPL34.SA'],
    }
    return render(request, "finances/symbols.html", context=context)

def new_user_form(request):
    return render(request, "finances/new_user_form.html")

def add_user(request):
    name = request.POST["name"]
    email = request.POST["email"]
    person = Person(name=name, email=email)
    person.save()
    return HttpResponseRedirect(reverse("finances:users"))

def add_user_stock(request):
    email = request.POST['email']
    person = Person.objects.get(email=email)
    stock_symbol = request.POST['stock_symbol']
    min_limit = request.POST['min_limit']
    max_limit = request.POST['max_limit']
    time_interval = request.POST['time_interval']
    ps = PersonStock(
        person=person, 
        stock_symbol=stock_symbol, 
        min_limit=min_limit, 
        max_limit=max_limit,
        time_interval=time_interval,
    )
    ps.save()
    return HttpResponseRedirect(reverse('finances:users'))

class UsersView(generic.ListView):
    model = Person
    template_name = "finances/users.html"
    context_object_name = "users"

class UserView(generic.DetailView):
    model = Person
    template_name = "finances/user.html"
    context_object_name = 'user'

def symbol(request, symbol):
    df = yf.download(symbol, period='1day', interval='1m')
    emails = list(map(lambda p: p.email, Person.objects.all()))

    graph_data = {
        'x': df.index.strftime('%H:%M').tolist(),
        'y': df['Close'].tolist(),
    }

    context = {
        'graph_data': json.dumps(graph_data),
        'symbol': symbol.upper(),
        'emails': emails,
    }

    return render(request, 'finances/symbol.html', context)
