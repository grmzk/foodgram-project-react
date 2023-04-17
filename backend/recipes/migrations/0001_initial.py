# Generated by Django 4.1 on 2023-04-17 09:36

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True, verbose_name='Название')),
                ('slug', models.SlugField(max_length=200, unique=True, verbose_name='Слаг')),
                ('color', models.CharField(max_length=7, unique=True, validators=[django.core.validators.RegexValidator(message='Нужен HEX-код, который должен начинаться с символа # и состоять только из букв от A до F и цифр. Максимальная длина кода, включая #, 7 символов (например: #F10ABC).', regex='^#[0-9A-F]{,6}$')], verbose_name='Цвет')),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
                'ordering': ['slug'],
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Название')),
                ('text', models.TextField(verbose_name='Описание')),
                ('cooking_time', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(limit_value=1, message='Время приготовления не может быть меньше 1 минуты!')], verbose_name='Время приготовления (мин.)')),
                ('image', models.ImageField(upload_to='recipes/', verbose_name='Картинка')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('in_favorite', models.ManyToManyField(blank=True, related_name='favorite', to=settings.AUTH_USER_MODEL, verbose_name='В избранном')),
                ('in_shopping_cart', models.ManyToManyField(blank=True, related_name='shopping_cart', to=settings.AUTH_USER_MODEL, verbose_name='В списке покупок')),
                ('tags', models.ManyToManyField(related_name='recipes', to='recipes.tag', verbose_name='Теги')),
            ],
            options={
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
                'ordering': ['name'],
            },
        ),
    ]
