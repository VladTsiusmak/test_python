from celery import shared_task

from apps.listing.tasks import update_listings_prices_task
from apps.payment.services import ExchangeRateService


@shared_task
def fetch_currency_rates_task():
    ExchangeRateService.fetch_currency_rates()
    update_listings_prices_task.delay()