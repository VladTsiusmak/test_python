from celery import shared_task

from apps.listing.services import ListingPriceService


@shared_task
def update_listings_prices_task():
    ListingPriceService.update_prices()


@shared_task
def update_one_listing_prices_task(listing_id):
    ListingPriceService.update_one_price(listing_id)


@shared_task
def send_report_email_task(listing_id, user_id, message):
    from apps.core.services.email_service import EmailService
    from apps.listing.models import Listing
    from apps.users.models import User

    listing = Listing.objects.get(id=listing_id)
    user = User.objects.get(id=user_id)
    EmailService.send_listing_report_email(listing, user, message)


@shared_task
def send_blocked_listing_email_task(listing_id):
    from apps.core.services.email_service import EmailService
    from apps.listing.models import Listing

    listing = Listing.objects.get(id=listing_id)
    EmailService.send_blocked_listing_email(listing)