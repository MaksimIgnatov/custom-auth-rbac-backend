from rest_framework import serializers

from permissions.models import Role, UserRole

from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя."""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
            'password_confirm'
        )
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                {"password": "Пароли не совпадают"}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения пользователя."""
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_active',
            'roles',
            'created_at'
        )
        read_only_fields = ('id', 'created_at')

    def get_roles(self, obj):
        """Получить роли пользователя."""
        user_roles = UserRole.objects.filter(
            user=obj
        ).select_related('role')
        return [user_role.role.name for user_role in user_roles]


class LoginSerializer(serializers.Serializer):
    """Сериализатор для входа в систему."""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError({
                    "email": "Пользователь с таким email не найден"
                })

            if not user.is_active:
                raise serializers.ValidationError({
                    "email": "Пользователь неактивен"
                })

            if not user.check_password(password):
                raise serializers.ValidationError({
                    "password": "Неверный пароль"
                })

            attrs['user'] = user
        else:
            raise serializers.ValidationError(
                "Необходимо указать email и пароль"
            )

        return attrs

