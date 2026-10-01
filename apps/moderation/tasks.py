from celery import shared_task

from apps.moderation.services import ModerationBadWords


@shared_task
def moderation_listings_task(listing_id):
    ModerationBadWords.moderation_bad_words(listing_id)