from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    password = serializers.CharField(max_length=150, write_only=True)

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

    def get_is_subscribed(self, user):
        current_user = self.context['request'].user
        return user.following.all().filter(user=current_user.id).exists()


class UserSetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=150, required=True,
                                         write_only=True)
    current_password = serializers.CharField(max_length=150, required=True,
                                             write_only=True)

    class Meta:
        fields = ['new_password', 'current_password']

    def validate_current_password(self, current_password):
        current_user = self.context['request'].user
        if not current_user.check_password(current_password):
            raise ValidationError('Неверный пароль!')
        return current_password
