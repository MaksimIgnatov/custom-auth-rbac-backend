from django.contrib.auth import login, logout
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import (
    LoginSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)


class RegisterView(generics.CreateAPIView):
    """Регистрация нового пользователя."""
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Генерируем JWT токены
        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Пользователь успешно зарегистрирован'
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Вход в систему."""
    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.validated_data['user']

        # Генерируем JWT токены
        refresh = RefreshToken.for_user(user)

        # Опционально: используем сессии Django
        login(request, user)

        response = Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Успешный вход в систему'
        }, status=status.HTTP_200_OK)

        # Устанавливаем cookie для sessionid (опционально)
        response.set_cookie(
            'sessionid',
            request.session.session_key,
            httponly=True,
            samesite='Lax'
        )

        return response

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Выход из системы."""
    try:
        # Если используется JWT, можно добавить токен в blacklist
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
    except Exception:
        pass

    # Выход из сессии Django
    logout(request)

    response = Response({
        'message': 'Успешный выход из системы'
    }, status=status.HTTP_200_OK)

    # Удаляем cookie
    response.delete_cookie('sessionid')

    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Получить профиль текущего пользователя."""
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)
