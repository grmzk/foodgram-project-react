from django.contrib import admin

from recipes.models import Recipe

from .models import User

admin.site.register(Recipe)
admin.site.register(User)
