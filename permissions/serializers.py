from rest_framework import serializers

from accounts.models import User

from .models import AccessRoleRule, BusinessElement, Role, UserRole


class RoleSerializer(serializers.ModelSerializer):
    """Сериализатор для ролей."""
    class Meta:
        model = Role
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class BusinessElementSerializer(serializers.ModelSerializer):
    """Сериализатор для бизнес-элементов."""
    class Meta:
        model = BusinessElement
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class AccessRoleRuleSerializer(serializers.ModelSerializer):
    """Сериализатор для правил доступа."""
    role_name = serializers.CharField(
        source='role.name',
        read_only=True
    )
    element_name = serializers.CharField(
        source='element.name',
        read_only=True
    )

    class Meta:
        model = AccessRoleRule
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class UserRoleSerializer(serializers.ModelSerializer):
    """Сериализатор для связи пользователей с ролями."""
    role_name = serializers.CharField(
        source='role.name',
        read_only=True
    )
    user_email = serializers.CharField(
        source='user.email',
        read_only=True
    )

    class Meta:
        model = UserRole
        fields = '__all__'
        read_only_fields = ('created_at',)


class AssignRoleSerializer(serializers.Serializer):
    """Сериализатор для назначения роли пользователю."""
    user_id = serializers.IntegerField()
    role_id = serializers.IntegerField()

    def validate(self, attrs):
        user_id = attrs.get('user_id')
        role_id = attrs.get('role_id')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                "user_id": "Пользователь не найден"
            })

        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            raise serializers.ValidationError({
                "role_id": "Роль не найдена"
            })

        attrs['user'] = user
        attrs['role'] = role

        return attrs

