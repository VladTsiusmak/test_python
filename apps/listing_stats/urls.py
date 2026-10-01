from django.urls import path

from apps.listing_stats.views import ListingStatsView

urlpatterns = [
    path('<int:pk>/', ListingStatsView.as_view(), name='statistics'),
]