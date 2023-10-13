from django.contrib import admin
from .models import User, Tunnel, Notification

admin.site.register(User)
admin.site.register(Tunnel)
admin.site.register(Notification)