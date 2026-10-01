from django.db import models

from apps.core.models import BaseModel


class CurrencyRate(BaseModel):
    class Meta:
        db_table = 'currency_rate'
        ordering = ['-date']

    date = models.DateField(unique=True)
    usd_to_uah = models.DecimalField(max_digits=10, decimal_places=4)
    eur_to_uah = models.DecimalField(max_digits=10, decimal_places=4)