from django.contrib import admin

from recipes.models import Recipe, Tag

from .models import User

admin.site.register(Recipe)
admin.site.register(Tag)
admin.site.register(User)
