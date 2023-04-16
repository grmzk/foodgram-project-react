from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import username_regex_validator


class User(AbstractUser):
    username = models.CharField(
        verbose_name='Юзернэйм',
        max_length=150,
        validators=[username_regex_validator],
        unique=True,
        blank=False,
    )
    email = models.EmailField(
        verbose_name='Почта',
        max_length=254,
        blank=False,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=False,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=False,
    )
