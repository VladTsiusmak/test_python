from django.db import models

from apps.core.models import BaseModel
from apps.listing.models import Listing
from apps.users.models import User


class ListingModeration(BaseModel):

    class Meta:
        db_table = 'listing_moderation'
        ordering = ['-created_at']

    class ModerationAction(models.TextChoices):
        CREATED = 'created', 'Створено'
        EDITED = 'edited', 'Відредаговано продавцем'
        AUTO_APPROVED = 'auto_approved', 'Автоматично схвалено'
        AUTO_REJECTED = 'auto_rejected', 'Автоматично відхилено'
        MANUAL_APPROVED = 'manual_approved', 'Схвалено менеджером'
        MANUAL_REJECTED = 'manual_rejected', 'Відхилено менеджером'

    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='moderation_logs',
    )

    moderation_action = models.CharField(
        max_length=20,
        choices=ModerationAction,
    )

    moderator = models.ForeignKey(
        User,
        related_name='moderated_listings',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    send_letter_at = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)