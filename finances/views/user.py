from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import generic

from ..models import User, Notification


class UsersPage(generic.ListView):
    model = User
    template_name = "finances/users.html"
    context_object_name = "users"

class UserPage(generic.DetailView):
    model = User
    template_name = "finances/user.html"
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tunnels = self.get_object().tunnel_set.all()
        context["tunnels"] = tunnels

        context["notifications"] = Notification.objects.filter(tunnel__user=self.get_object())
        return context
    
def user_form_page(request):
    return render(request, "finances/user_form.html")

def add_user(request):
    name = request.POST["name"]
    email = request.POST["email"]
    user = User(name=name, email=email)
    user.save()
    return HttpResponseRedirect(reverse("finances:users"))

