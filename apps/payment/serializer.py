from rest_framework import serializers

from apps.payment.models import CurrencyRate


class CurrencyRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyRate
        fields = (
            'date',
            'usd_to_uah',
            'eur_to_uah',
        )