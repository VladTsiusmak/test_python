from django.utils import timezone

import requests

from apps.payment.models import CurrencyRate


class ExchangeRateService:

    @staticmethod
    def fetch_currency_rates():

        response = requests.get('https://api.privatbank.ua/p24api/pubinfo?exchange&coursid=5')
        if response.status_code == 200:
            data = response.json()

            usd_rate = None
            euro_rate = None

            for currency in data:
                if currency['ccy'] == 'USD':
                    usd_rate = currency['sale']
                if currency['ccy'] == 'EUR':
                    euro_rate = currency['sale']

            today = timezone.now().date()

            CurrencyRate.objects.update_or_create(
                date=today,
                defaults={
                    'usd_to_uah': usd_rate,
                    'eur_to_uah': euro_rate
                }
            )

            return usd_rate, euro_rate
        else:
            raise Exception(f"Error fetching currency rates: {response.status_code}")