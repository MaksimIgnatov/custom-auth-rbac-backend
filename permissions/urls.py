from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RoleViewSet,
    BusinessElementViewSet,
    AccessRoleRuleViewSet,
    UserRoleViewSet
)

app_name = 'permissions'

router = DefaultRouter()
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'business-elements', BusinessElementViewSet, basename='business-element')
router.register(r'access-rules', AccessRoleRuleViewSet, basename='access-rule')
router.register(r'user-roles', UserRoleViewSet, basename='user-role')

urlpatterns = [
    path('', include(router.urls)),
]

