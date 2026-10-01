from rest_framework import serializers

from apps.cars.models import Brand, CarModel


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ('id', 'name')
        read_only_fields = ('id',)

class CarModelReadSerializer(serializers.ModelSerializer):
    brand = BrandSerializer(read_only=True)
    class Meta:
        model = CarModel
        fields = ['id', 'brand', 'name']

class CarModelWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarModel
        fields = ['id', 'brand', 'name']
        read_only_fields = ('id',)

class SendEmailSerializer(serializers.Serializer):
    message = serializers.CharField(
        max_length=1000,
        trim_whitespace=True,
    )