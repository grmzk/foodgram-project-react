from django.contrib import admin

from recipes.models import (Favorite, Ingredient, IngredientRecipe,
                            MeasurementUnit, Recipe, ShoppingCart, Tag)

admin.site.register(Tag)
admin.site.register(MeasurementUnit)
admin.site.register(ShoppingCart)
admin.site.register(Favorite)
admin.site.register(IngredientRecipe)


class IngredientRecipeInlineAdmin(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_filter = ['author__username', 'name', 'tags__name']
    search_fields = list_filter
    list_display = ['name', 'author']
    fields = ['pub_date', 'name', 'text', 'cooking_time', 'image', 'author',
              'tags', 'in_favorite_count']
    readonly_fields = ['pub_date', 'in_favorite_count']
    inlines = [IngredientRecipeInlineAdmin]

    @staticmethod
    def in_favorite_count(obj):
        return obj.favorite.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_filter = ['name']
    search_fields = list_filter
    list_display = ['name', 'measurement_unit']
