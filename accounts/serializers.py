from rest_framework.serializers import ModelSerializer

from .models import User


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "full_name",
            "alias_name",
            "user_type",
            "is_active",
        )
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data.pop('username'),
            password=validated_data.pop('password'),
            **validated_data
        )
