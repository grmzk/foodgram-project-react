from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class UserSetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=150,
                                         required=True,
                                         write_only=True,
                                         validators=[validate_password])
    current_password = serializers.CharField(max_length=150, required=True,
                                             write_only=True)

    class Meta:
        fields = ['new_password', 'current_password']

    def validate_current_password(self, current_password):
        current_user = self.context['request'].user
        if not current_user.check_password(current_password):
            raise ValidationError('Неверный пароль!')
        return current_password
