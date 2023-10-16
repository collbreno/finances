from django.urls import path

from .views import user, tunnel, home, stock

app_name = "finances"
urlpatterns = [
    path("", home.index_page, name="index"),

    path("users/", user.UsersPage.as_view(), name="users"),
    path("users/<str:pk>/", user.UserPage.as_view(), name="user"),
    path("user_form/", user.user_form_page, name="user_form"),
    path("add_user/", user.add_user, name="add_user"),

    path("stocks/<str:stock_symbol>/", stock.stock_page, name="stock"),
    path("stocks/", stock.stocks_page, name="stocks"),
    path("get_symbol_suggestions/", stock.get_symbol_suggestions, name="get_symbol_suggestions"),

    path("stocks/<str:stock_symbol>/tunnel_form/", tunnel.tunnel_form_page, name="tunnel_form"),
    path("add_tunnel/", tunnel.add_tunnel, name="add_tunnel"),
    path("delete_tunnel/", tunnel.delete_tunnel, name="delete_tunnel"),
]