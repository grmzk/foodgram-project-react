from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from users.models import User
from users.validators import username_regex_validator


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150,
                                     validators=[username_regex_validator])
    is_subscribed = serializers.BooleanField(read_only=True)
    password = serializers.CharField(max_length=150, write_only=True,
                                     validators=[validate_password])

    class Meta:
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'password', 'is_subscribed']
        model = User

    def get_fields(self):
        fields = super().get_fields()
        method = self.context['request'].method
        if method == 'POST':
            del fields['is_subscribed']
        return fields

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
