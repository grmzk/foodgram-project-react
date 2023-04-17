from django.contrib import admin

from recipes.models import Ingredient, MeasurementUnit, Recipe, Tag

from .models import Subscription, User

admin.site.register(User)
admin.site.register(Subscription)
admin.site.register(Tag)
admin.site.register(Recipe)
admin.site.register(MeasurementUnit)
admin.site.register(Ingredient)
