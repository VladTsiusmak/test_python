from django.db import transaction
from rest_framework import serializers

from apps.users.models import Role, Profile, User


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']
        read_only_fields = ('id',)


class ProfileReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'name', 'logo', 'description', 'type_profile', 'account_type', 'account_expires_at']


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['name', 'logo', 'description']


class ProfileUpgradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['account_type', 'account_expires_at']


class UserReadSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    profile = ProfileReadSerializer()

    class Meta:
        model = User
        fields = ['id', 'profile', 'avatar', 'role', 'phone', 'deleted_at']
        read_only_fields = ('id', 'role', 'deleted_at')


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    profile = ProfileUpdateSerializer()

    class Meta:
        model = User
        fields = ['avatar', 'phone', 'profile']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})

        with transaction.atomic():
            instance.super().update(instance, validated_data)

            if profile_data and instance.profile:
                profile_serializer = ProfileUpdateSerializer(
                    instance.profile,
                    data=profile_data,
                    partial=True
                )
                profile_serializer.is_valid(raise_exception=True)
                profile_serializer.save()
            return instance
