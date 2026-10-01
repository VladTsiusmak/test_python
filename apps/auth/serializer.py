import re

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction

from rest_framework import serializers

from apps.users.models import Profile, Role

UserModel = get_user_model()


class RegisterSerializer(serializers.Serializer):

    email = serializers.EmailField(help_text="User's unique email")
    password = serializers.CharField(
        write_only=True,
        help_text="Password (minimum 8 characters)"
    )
    confirm_password = serializers.CharField(
        write_only=True,
        help_text="Password confirmation"
    )
    phone = serializers.CharField(
        write_only=True,
        help_text="User's phone number in the format +380XXXXXXXXX"
    )
    role = serializers.ChoiceField(
        choices=[
            Role.RoleName.BUYER,
            Role.RoleName.SELLER,
        ],
        write_only=True,
        help_text="User role: buyer або seller"
    )

    def validate_email(self, value):
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, value):
            raise serializers.ValidationError("Invalid email format")
        return value.lower()

    def validate_phone(self, value):
        phone_regex = r'^\+380\d{9}$'
        if not re.match(phone_regex, value):
            raise serializers.ValidationError(
                "Phone number must be in format +380XXXXXXXXX"
            )
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords don't match."}
            )

        try:
            validate_password(data["password"])
        except DjangoValidationError as e:
            raise serializers.ValidationError(
                {"password": list(e.messages)}
            )

        if UserModel.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError(
                {"email": "Email already exists."}
            )

        if UserModel.objects.filter(phone=data['phone']).exists():
            raise serializers.ValidationError(
                {"phone": "Phone already exists."}
            )

        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')

        with transaction.atomic():
            user = UserModel.objects.create_user(
                email=validated_data['email'],
                username=validated_data['email'],
                password=validated_data['password'],
                phone=validated_data['phone'],
            )

            role_name = validated_data.get('role', Role.RoleName.BUYER)
            user.role = Role.objects.get(name=role_name)

            profile = Profile.objects.create(name=validated_data['email'])
            user.profile = profile

            user.save(update_fields=['role', 'profile'])

        return user