from celery import shared_task

from apps.core.services.email_service import EmailService
from apps.users.models import User


@shared_task
def send_offer_new_carmodel_task(user_id, message):

    user = User.objects.get(id=user_id)
    EmailService.send_email_about_new_carmodel(user, message)