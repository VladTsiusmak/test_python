from datetime import timedelta

from django.db.models import Avg
from django.utils import timezone

from apps.listing.models import Listing
from apps.listing_stats.models import ListingStats


class ListingStatsService:
    @staticmethod
    def get_stats(listing) -> dict:
        now = timezone.now()
        day_ago = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        views_qs = ListingStats.objects.filter(listing=listing)
        views_total = views_qs.count()
        views_day = views_qs.filter(created_at__gte=day_ago).count()
        views_week = views_qs.filter(created_at__gte=week_ago).count()
        views_month = views_qs.filter(created_at__gte=month_ago).count()

        avg_price_ukraine = (
            Listing.objects.filter(
                car_model=listing.car_model,
                status=Listing.ListingStatus.ACTIVE
            )
            .aggregate(avg_price=Avg('price_usd'))
            ['avg_price']
        )


        avg_price_region = (
            Listing.objects.filter(
                car_model=listing.car_model,
                region=listing.region,
                status=Listing.ListingStatus.ACTIVE
            )
            .aggregate(avg_price=Avg('price_usd'))
            ['avg_price']
        )

        return {
            'id': listing.id,
            'views_day': views_day,
            'views_week': views_week,
            'views_month': views_month,
            'views_total': views_total,
            'avg_price_ukraine': avg_price_ukraine,
            'avg_price_region': avg_price_region,
        }