from django.urls import path

from apps.payment.views import CurrencyRateView

urlpatterns = [
    path('rate/', CurrencyRateView.as_view(), name='payment')
]