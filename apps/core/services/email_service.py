import os

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template


class EmailService:
    @staticmethod
    def _send_email(to:str, template_name:str, context:dict, subject:str):
         template = get_template(template_name)
         html_message = template.render(context)

         msg = EmailMultiAlternatives(
             to=[to],
             from_email=os.environ.get('EMAIL_HOST_USER'),
             subject=subject,
         )
         msg.attach_alternative(html_message, "text/html")
         msg.send()
    @staticmethod
    def send_blocked_listing_email(listing):
        EmailService._send_email(
            to=os.environ.get('MANAGERS_EMAIL', 'moderation@automarket.com'),
            template_name='moderation/blocked_listing.html',
            context={
                'owner_name': listing.owner.username,
                'listing_id': listing.id,
                'car': str(listing.car_model),
            },
            subject='Оголошення заблоковано'
        )
    @staticmethod
    def send_email_about_new_carmodel(user, message:str):
        EmailService._send_email(
            to=os.environ.get('MANAGERS_EMAIL', 'moderation@automarket.com'),
            template_name='cars/about_new_carmodel.html',
            context={
                'owner_name': user.username,
                'message': message,
            },
            subject='Запит на додавання нової марки/моделі авто'
        )
    @staticmethod
    def send_listing_report_email(listing, user, message:str):
        EmailService._send_email(
            to=os.environ.get('MANAGERS_EMAIL', 'moderation@automarket.com'),
            template_name='listings/about_problem.html',
            context={
                'owner_name': user.username,
                'listing_id': listing.id,
                'message': message,
            },
            subject='Скарга на оголошення'
        )