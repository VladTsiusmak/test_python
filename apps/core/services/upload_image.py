import os
from uuid import uuid4

def upload_listing_image(instance, filename):
    ext = filename.split('.')[-1]
    return os.path.join('listings_images', str(instance.listing_id), f'{uuid4()}.{ext}')

def upload_avatar(instance, filename):
    ext = filename.split('.')[-1]
    return os.path.join('avatars', str(instance.id), f'{uuid4()}.{ext}')

def upload_profile_logo(instance, filename):
    ext = filename.split('.')[-1]
    return os.path.join('profile_logos', str(instance.id), f'{uuid4()}.{ext}')