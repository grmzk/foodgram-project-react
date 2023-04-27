from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Subscription, User

admin.site.register(Subscription)


@admin.register(User)
class UserAdmin(UserAdmin):
    list_filter = ['username', 'email']
    search_fields = list_filter
