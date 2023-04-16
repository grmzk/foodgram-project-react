from django.db import models

from users.models import User

from .validators import min_cooking_time_validator, color_hex_validator


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        unique=True,
        blank=False,
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=200,
        unique=True,
        blank=False,
    )
    color = models.CharField(
        verbose_name='Цвет',
        max_length=7,
        validators=[color_hex_validator],
        unique=True,
        blank=False,
    )


class Recipe(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        blank=False,
    )
    text = models.TextField(
        verbose_name='Описание',
        blank=False,
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (мин.)',
        validators=[min_cooking_time_validator],
        blank=False,
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/',
        blank=False,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='recipes',
        on_delete=models.CASCADE,
        blank=False,
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes',
        blank=False
    )
    # ingredients = None
    # favorite = None
    # in_shopping_cart = None

