from django.core.validators import RegexValidator

username_regex_validator = RegexValidator(
    regex=r'^[\w@+\-.]+$',
    message='<username> может состоять только из '
            'букв, цифр и символов: .@+-_'
)
