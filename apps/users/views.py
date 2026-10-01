import datetime

from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema

from apps.core.permissions.permissions import HasPermissionCodename
from apps.users.models import Profile, Role
from apps.users.serializer import UserReadSerializer, UserProfileUpdateSerializer, ProfileUpgradeSerializer

UserModel = get_user_model()


@extend_schema(
    summary="Отримати список користувачів",
    description="Адміністратор має повний доступ. Менеджер бачить лише покупців і продавців",
)
class UserListView(generics.ListAPIView):
    serializer_class = UserReadSerializer
    permission_classes = [HasPermissionCodename]
    required_permission = 'can_view_users'

    def get_queryset(self):
        qs = UserModel.objects.select_related('profile', 'role')
        if not self.request.user.is_superuser:
            qs = qs.filter(is_superuser=False).exclude(role__name=Role.RoleName.MANAGER)
        return qs


@extend_schema(
    summary="Отримати акаунт користувача",
    description="Перегляд даних конкретного користувача по ID.",
)
class UserDetailView(generics.RetrieveAPIView):
    serializer_class = UserReadSerializer
    permission_classes = [HasPermissionCodename]
    required_permission = 'can_view_user_by_id'

    def get_queryset(self):
        qs = UserModel.objects.select_related('profile', 'role').all()
        # Менеджери не бачать адмінів
        if not self.request.user.is_superuser:
            qs = qs.filter(is_superuser=False)
        return qs


@extend_schema(
    summary="Видалити користувача",
    description="М'яке видалення користувача по ID.",
)
class UserDeleteView(generics.DestroyAPIView):
    queryset = UserModel.objects.select_related('profile', 'role').filter(deleted_at__isnull=True)
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [HasPermissionCodename]
    required_permission = 'can_delete_user_by_id'

    def destroy(self, *args, **kwargs):
        user = self.get_object()

        if user == self.request.user:
            return Response(
                {'message': 'You cannot delete yourself.'},
                status=status.HTTP_403_FORBIDDEN
            )

        if user.is_superuser or (user.role and user.role.name == Role.RoleName.ADMIN):
            return Response(
                {'message': 'You cannot delete admin.'},
                status=status.HTTP_403_FORBIDDEN
            )

        if user.role and user.role.name == Role.RoleName.MANAGER and not self.request.user.is_superuser:
            return Response(
                {'message': 'You cannot delete another manager.'},
                status=status.HTTP_403_FORBIDDEN
            )

        user.soft_delete()
        return Response(
            {'message': 'User account has been deleted.'},
            status=status.HTTP_200_OK
        )


@extend_schema(
    summary="Отримати власний акаунт",
    description="Доступно лише власнику.",
)
class UserMeView(generics.RetrieveAPIView):
    permission_classes = [HasPermissionCodename]
    serializer_class = UserReadSerializer
    required_permission = 'can_view_own_account'

    def get_object(self):
        return self.request.user


@extend_schema(
    summary="Оновити власний акаунт",
    description="Часткове оновлення власного акаунту.",
)
class UserMeUpdateView(generics.UpdateAPIView):
    permission_classes = [HasPermissionCodename]
    serializer_class = UserProfileUpdateSerializer
    required_permission = 'can_update_own_account'
    http_method_names = ['patch']

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        user = self.request.user
        # Автоматичне створення профілю для суперадміна (якщо відсутній)
        profile = getattr(user, 'profile', None)
        if profile is None:
            profile = Profile.objects.create(name=user.username)
            user.profile = profile
            user.save(update_fields=['profile'])
        serializer.save()


@extend_schema(
    summary="Видалити власний акаунт",
    description="М'яке видалення власного акаунту.",
)
class UserMeDeleteView(generics.DestroyAPIView):
    permission_classes = [HasPermissionCodename]
    serializer_class = UserProfileUpdateSerializer
    required_permission = 'can_delete_own_account'

    def get_object(self):
        return self.request.user

    def destroy(self, *args, **kwargs):
        user = self.get_object()
        if user.is_superuser:
            return Response(
                {"detail": "Administrator account cannot be deleted."},
                status=status.HTTP_403_FORBIDDEN,
            )
        user.soft_delete()
        return Response(
            {'message': 'User account has been deleted.'},
            status=status.HTTP_200_OK
        )


@extend_schema(
    summary="Заблокувати користувача",
    description="Блокування акаунту по ID.",
)
class UserBlockView(GenericAPIView):
    queryset = UserModel.objects.select_related('profile', 'role').all()
    permission_classes = [HasPermissionCodename]
    required_permission = 'can_block_unblock_user'

    def get_object(self):
        return get_object_or_404(self.get_queryset(), pk=self.kwargs['pk'])

    def patch(self, request, *args, **kwargs):
        user = self.get_object()

        if user == request.user:
            return Response(
                {'message': 'You cannot block yourself.'},
                status=status.HTTP_403_FORBIDDEN
            )

        if user.is_superuser or (user.role and user.role.name == Role.RoleName.ADMIN):
            return Response(
                {'message': 'You cannot block admin.'},
                status=status.HTTP_403_FORBIDDEN
            )

        if user.role and user.role.name == Role.RoleName.MANAGER and not self.request.user.is_superuser:
            return Response(
                {'message': 'You cannot block another manager.'},
                status=status.HTTP_403_FORBIDDEN
            )

        user.is_active = False
        user.save(update_fields=['is_active'])

        return Response(
            {
                'message': 'User has been blocked.',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'is_active': user.is_active,
                    'profile': {
                        'name': user.profile.name if user.profile else None,
                        'type': user.profile.type_profile if user.profile else None,
                        'account_type': user.profile.account_type if user.profile else None,
                    }
                }
            },
            status=status.HTTP_200_OK
        )


@extend_schema(
    summary="Розблокувати користувача",
    description="Розблокування акаунту по ID.",
)
class UserUnblockView(generics.GenericAPIView):
    queryset = UserModel.objects.select_related('profile', 'role').all()
    permission_classes = [HasPermissionCodename]
    required_permission = 'can_block_unblock_user'

    def get_object(self):
        return get_object_or_404(self.get_queryset(), pk=self.kwargs['pk'])

    def patch(self, request, *args, **kwargs):
        user = self.get_object()

        if user.is_superuser or (user.role and user.role.name == Role.RoleName.ADMIN):
            return Response(
                {'message': 'You cannot unblock admin.'},
                status=status.HTTP_403_FORBIDDEN
            )

        if user.role and user.role.name == Role.RoleName.MANAGER and not self.request.user.is_superuser:
            return Response(
                {'message': 'You cannot unblock another manager.'},
                status=status.HTTP_403_FORBIDDEN
            )

        user.is_active = True
        user.save(update_fields=['is_active'])

        return Response(
            {
                'message': 'User has been unblocked',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'is_active': user.is_active,
                    'profile': {
                        'name': user.profile.name if user.profile else None,
                        'type': user.profile.type_profile if user.profile else None,
                        'account_type': user.profile.account_type if user.profile else None,
                    }
                }
            },
            status=status.HTTP_200_OK
        )


@extend_schema(
    summary="Призначити менеджера",
    description="Перетворює користувача на менеджера по ID.",
)
class UserToManagerView(GenericAPIView):
    queryset = UserModel.objects.select_related('profile', 'role').all()
    permission_classes = [HasPermissionCodename]
    required_permission = 'can_create_manager'

    def get_object(self):
        return get_object_or_404(self.get_queryset(), pk=self.kwargs['pk'])

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        manager_role = get_object_or_404(Role, name=Role.RoleName.MANAGER)
        user.role = manager_role
        user.save()
        serializer = UserReadSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="Надати преміум акаунт",
    description="Активація преміум-статусу на 30 днів (заглушка).",
)
class UserToPremiumView(GenericAPIView):
    permission_classes = [HasPermissionCodename]
    required_permission = 'can_be_premium_user'
    serializer_class = ProfileUpgradeSerializer

    def post(self, request, *args, **kwargs):
        profile = request.user.profile

        if profile is None:
            return Response(
                {"detail": "User profile was not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        profile.account_type = Profile.AccountType.PREMIUM
        profile.account_expires_at = timezone.now() + datetime.timedelta(days=30)
        profile.save(update_fields=['account_type', 'account_expires_at'])

        serializer = self.get_serializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)