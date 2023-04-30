from rest_framework.exceptions import ValidationError


def integer_validator(name, value):
    try:
        value = int(value)
    except ValueError:
        raise ValidationError(f'Value `{name}` must be integer!')
    return value
