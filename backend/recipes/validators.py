from django.core.validators import MinValueValidator


min_cooking_time_validator = MinValueValidator(
    limit_value=1,
    message='Время приготовления не может быть меньше 1 минуты!'
)
