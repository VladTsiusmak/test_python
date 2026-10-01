from django.db import models

from apps.core.models import BaseModel
from apps.listing.models import Listing
from apps.users.models import User


class ListingStats(BaseModel):
    class Meta:
        db_table = 'listing_stats'
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['listing']),
            models.Index(fields=['listing', 'created_at']),
        ]

    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='view',
    )

    viewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )