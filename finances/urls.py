from django.urls import path

from . import views

app_name = "finances"
urlpatterns = [
    path("", views.index, name="index"),
    path("newuser/", views.new_user_form, name="new_user_form"),
    path("users/", views.UsersView.as_view(), name="users"),
    path("users/<str:pk>/", views.UserView.as_view(), name="user"),
    path("add_user/", views.add_user, name="add_user"),
    path("add_user_stock/", views.add_user_stock, name="add_user_stock"),
    path("symbols/", views.symbols, name="symbols"),
    path("symbols/<str:symbol>", views.symbol, name="symbol")
]