from django.db import models
from .validators import min_cooking_time_validator


class Recipe(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        blank=False
    )
    text = models.TextField(
        verbose_name='Описание',
        blank=False
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления (мин.)',
        validators=[min_cooking_time_validator],
        blank=False
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/',
        blank=False
    )
    # author = None
    # ingredients = None
    # tags = None
    # favorite = None
    # in_shopping_cart = None
