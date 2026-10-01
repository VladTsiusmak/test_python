import django_filters

from apps.listing.models import Region, Listing


class ListingFilter(django_filters.FilterSet):
    region = django_filters.ModelChoiceFilter(queryset=Region.objects.all())
    body_type = django_filters.ChoiceFilter(choices=Listing.BodyType.choices)
    condition_type = django_filters.ChoiceFilter(choices=Listing.CarConditions.choices)
    fuel_type = django_filters.ChoiceFilter(choices=Listing.FuelType.choices)
    transmission_type = django_filters.ChoiceFilter(choices=Listing.TransmissionType.choices)
    drive_type = django_filters.ChoiceFilter(choices=Listing.DriveType.choices)


    price_usd_min = django_filters.NumberFilter(field_name='price_usd', lookup_expr='gte')
    price_usd_max = django_filters.NumberFilter(field_name='price_usd', lookup_expr='lte')
    price_eur_min = django_filters.NumberFilter(field_name='price_eur', lookup_expr='gte')
    price_eur_max = django_filters.NumberFilter(field_name='price_eur', lookup_expr='lte')
    price_uah_min = django_filters.NumberFilter(field_name='price_uah', lookup_expr='gte')
    price_uah_max = django_filters.NumberFilter(field_name='price_uah', lookup_expr='lte')


    mileage_min = django_filters.NumberFilter(field_name='mileage', lookup_expr='gte')
    mileage_max = django_filters.NumberFilter(field_name='mileage', lookup_expr='lte')
    year_min = django_filters.NumberFilter(field_name='year', lookup_expr='gte')
    year_max = django_filters.NumberFilter(field_name='year', lookup_expr='lte')

    class Meta:
        model = Listing
        fields = []
