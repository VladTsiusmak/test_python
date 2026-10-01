import django_filters

from apps.listing.models import Listing


class MyListingFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(
        choices=Listing.ListingStatus.choices,
    )

    class Meta:
        model = Listing
        fields = ['status']