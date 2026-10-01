from apps.listing.models import Listing
from apps.moderation.bad_words import BAD_WORDS
from apps.moderation.models import ListingModeration


class ModerationBadWords:

    @staticmethod
    def moderation_bad_words(listing_id):
        listing = Listing.objects.get(id=listing_id)

        text = f'{listing.description} {listing.color}'
        has_bad_words = any(word in text.lower() for word in BAD_WORDS)

        if has_bad_words:
            listing.status = Listing.ListingStatus.REJECTED
            moderation_action = ListingModeration.ModerationAction.AUTO_REJECTED
        else:
            listing.status = Listing.ListingStatus.ACTIVE
            moderation_action = ListingModeration.ModerationAction.AUTO_APPROVED

        listing.save(update_fields=['status'])

        ListingModeration.objects.create(
            listing=listing,
            moderation_action=moderation_action,
        )