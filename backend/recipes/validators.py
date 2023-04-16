from django.core.validators import MinValueValidator, RegexValidator

min_cooking_time_validator = MinValueValidator(
    limit_value=1,
    message='Время приготовления не может быть меньше 1 минуты!'
)
color_hex_validator = RegexValidator(
    regex=r'^#[0-9A-F]{,6}$',
    message='Нужен HEX-код, который должен начинаться с символа # '
            'и состоять только из букв от A до F и цифр. '
            'Максимальная длина кода, включая #, '
            '7 символов (например: #F10ABC).'
)
