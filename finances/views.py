import yfinance as yf

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from requests.exceptions import HTTPError
from django.urls import reverse
from django.views import generic

from .models import Person

def index(request):
    return render(request, "finances/index.html")

def symbols(requests):
    return HttpResponse('lista de simbolos')

def new_user_form(request):
    return render(request, "finances/new_user_form.html")

def add_user(request):
    name = request.POST["name"]
    email = request.POST["email"]
    person = Person(name=name, email=email)
    person.save()
    return HttpResponseRedirect(reverse("finances:users"))

class UsersView(generic.ListView):
    model = Person
    template_name = "finances/users.html"
    context_object_name = "users"

class UserView(generic.DetailView):
    model = Person
    template_name = "finances/user.html"
    context_object_name = 'user'

def symbol(request, symbol):
    try:
        ticker = yf.Ticker(symbol)
    except HTTPError:
        return HttpResponse(f"{symbol} not found")
    price = ticker.info["currentPrice"]
    short_name = ticker.info["shortName"]
    long_name = ticker.info["longName"]
    currency = ticker.info["currency"]
    return HttpResponse(f"vc esta vendo a acao {symbol} \nEmpresa: {long_name}\nValor: {price} {currency}")