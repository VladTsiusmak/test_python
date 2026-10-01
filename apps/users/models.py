from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone

from apps.core.models import BaseModel
from apps.core.services.upload_image import upload_avatar, upload_profile_logo


class CustomPermission(models.Model):
    class Meta:
        db_table = 'custom_permission'

    name = models.CharField(max_length=100)
    codename = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Role(models.Model):
    class Meta:
        db_table = 'role'

    class RoleName(models.TextChoices):
        BUYER = 'buyer', 'Покупець'
        SELLER = 'seller', 'Продавець'
        MANAGER = 'manager', 'Менеджер'
        ADMIN = 'admin', 'Адміністратор'

    name = models.CharField(max_length=50, unique=True)
    permissions = models.ManyToManyField(CustomPermission, through='RolePermissions')

    def __str__(self):
        return self.name


class Profile(BaseModel):
    class Meta:
        db_table = 'profile'
        indexes = [
            models.Index(fields=['type_profile'], name='profile_type_idx'),
            models.Index(fields=['account_type'], name='profile_account_type_idx'),
        ]

    class TypeProfile(models.TextChoices):
        INDIVIDUAL = 'individual', 'Одиночний користувач'
        DEALER = 'dealer', 'Автосалон'

    class AccountType(models.TextChoices):
        BASIC = 'basic', 'Базовий'
        PREMIUM = 'premium', 'Преміум'

    type_profile = models.CharField(
        max_length=20,
        choices=TypeProfile,
        default=TypeProfile.INDIVIDUAL
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, help_text='Інформація про продавця')
    logo = models.ImageField(upload_to=upload_profile_logo, blank=True, null=True)

    account_type = models.CharField(
        max_length=20,
        choices=AccountType,
        default=AccountType.BASIC
    )
    account_expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} [{self.get_type_profile_display()}]"


class UserManager(BaseUserManager):
    def create_user(self, username, phone, password=None, **extra_fields):
        if not username:
            raise ValueError("Username is required")
        if not phone:
            raise ValueError("Phone is required")

        user = self.model(
            username=username,
            phone=phone,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        admin_role = Role.objects.get(name=Role.RoleName.ADMIN)
        extra_fields["role"] = admin_role

        return self.create_user(
            username=username,
            phone=phone,
            password=password,
            **extra_fields
        )


class User(AbstractUser, BaseModel):
    class Meta:
        db_table = 'user'
        ordering = ['id']

    objects = UserManager()

    phone = models.CharField(max_length=20, unique=True)
    avatar = models.ImageField(upload_to=upload_avatar, blank=True, null=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    profile = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members',
    )

    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
    )

    REQUIRED_FIELDS = ['phone']

    def __str__(self):
        return f"{self.username} ({self.role.name if self.role else 'Без ролі'})"

    def soft_delete(self):
        if not self.deleted_at:
            self.is_active = False
            self.deleted_at = timezone.now()
            self.save(update_fields=['is_active', 'deleted_at'])

    def restore(self):
        self.is_active = True
        self.deleted_at = None
        self.save(update_fields=['is_active', 'deleted_at'])


class RolePermissions(models.Model):
    class Meta:
        db_table = 'role_permissions'
        constraints = [
            models.UniqueConstraint(
                fields=['role', 'permission'],
                name='unique_role_permission'
            )
        ]

    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='role_permissions'
    )
    permission = models.ForeignKey(
        CustomPermission,
        on_delete=models.CASCADE,
        related_name='permission_role_junction'
    )