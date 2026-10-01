from rest_framework import serializers


class ListingStatsSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    views_total = serializers.IntegerField(read_only=True)
    views_day = serializers.IntegerField(read_only=True)
    views_week = serializers.IntegerField(read_only=True)
    views_month = serializers.IntegerField(read_only=True)
    avg_price_region = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        allow_null=True,
        read_only=True
    )
    avg_price_ukraine = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        allow_null=True,
        read_only=True
    )