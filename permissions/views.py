from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import AccessRoleRule, BusinessElement, Role, UserRole
from .permissions import HasPermission
from .serializers import (
    AccessRoleRuleSerializer,
    AssignRoleSerializer,
    BusinessElementSerializer,
    RoleSerializer,
    UserRoleSerializer,
)


class RoleViewSet(viewsets.ModelViewSet):
    """ViewSet для управления ролями."""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    business_element = 'roles'


class BusinessElementViewSet(viewsets.ModelViewSet):
    """ViewSet для управления бизнес-элементами."""
    queryset = BusinessElement.objects.all()
    serializer_class = BusinessElementSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    business_element = 'business_elements'


class AccessRoleRuleViewSet(viewsets.ModelViewSet):
    """ViewSet для управления правилами доступа."""
    queryset = AccessRoleRule.objects.select_related(
        'role',
        'element'
    ).all()
    serializer_class = AccessRoleRuleSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    business_element = 'access_rules'


class UserRoleViewSet(viewsets.ModelViewSet):
    """ViewSet для управления ролями пользователей."""
    queryset = UserRole.objects.select_related('user', 'role').all()
    serializer_class = UserRoleSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    business_element = 'user_roles'

    @action(detail=False, methods=['post'], url_path='assign')
    def assign_role(self, request):
        """Назначить роль пользователю."""
        serializer = AssignRoleSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            role = serializer.validated_data['role']

            user_role, created = UserRole.objects.get_or_create(
                user=user,
                role=role
            )

            if created:
                return Response({
                    'message': (
                        f'Роль {role.name} успешно назначена '
                        f'пользователю {user.email}'
                    ),
                    'user_role': UserRoleSerializer(user_role).data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'message': (
                        f'Роль {role.name} уже назначена '
                        f'пользователю {user.email}'
                    ),
                    'user_role': UserRoleSerializer(user_role).data
                }, status=status.HTTP_200_OK)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['delete'], url_path='remove')
    def remove_role(self, request):
        """Удалить роль у пользователя."""
        user_id = request.data.get('user_id')
        role_id = request.data.get('role_id')

        if not user_id or not role_id:
            return Response(
                {'error': 'Необходимо указать user_id и role_id'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user_role = UserRole.objects.get(
                user_id=user_id,
                role_id=role_id
            )
            user_role.delete()
            return Response({
                'message': 'Роль успешно удалена у пользователя'
            }, status=status.HTTP_200_OK)
        except UserRole.DoesNotExist:
            return Response(
                {'error': 'Связь пользователя с ролью не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )
