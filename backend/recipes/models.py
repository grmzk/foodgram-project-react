from django.db import models

from users.models import User

from .validators import (color_hex_validator, min_amount_validator,
                         min_cooking_time_validator)


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

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['slug']

    def __str__(self):
        return f'{self.slug} [{self.name}]'


class MeasurementUnit(models.Model):
    name = models.CharField(
        verbose_name='Единица измерения',
        max_length=200,
        unique=True,
        blank=False,
    )

    class Meta:
        verbose_name = 'Единица измерения'
        verbose_name_plural = 'Единицы измерения'
        ordering = ['name']

    def __str__(self):
        return f'{self.name}'


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=200,
        unique=True,
        blank=False,
    )
    measurement_unit = models.ForeignKey(
        MeasurementUnit,
        verbose_name='Единица измерения',
        related_name='ingredients',
        on_delete=models.CASCADE,
        blank=False,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} [{self.measurement_unit}]'


class IngredientAmount(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        related_name='ingredient_amounts',
        on_delete=models.CASCADE,
        blank=False,
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=[min_amount_validator],
        blank=False,
    )

    class Meta:
        verbose_name = 'Ингредиент с количеством'
        verbose_name_plural = 'Ингредиенты с количеством'
        ordering = ['ingredient']

    def __str__(self):
        return (f'{self.ingredient.name} - {self.amount} '
                f'{self.ingredient.measurement_unit.name}')


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
    cooking_time = models.PositiveIntegerField(
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
    in_shopping_cart = models.ManyToManyField(
        User,
        verbose_name='В списке покупок',
        related_name='shopping_cart',
        blank=True,
    )
    in_favorite = models.ManyToManyField(
        User,
        verbose_name='В избранном',
        related_name='favorite',
        blank=True,
    )
    ingredients = models.ManyToManyField(
        IngredientAmount,
        verbose_name='Ингредиенты',
        related_name='recipes',
        blank=True,
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return f'Рецепт "{self.name}"'
