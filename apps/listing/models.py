from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from apps.cars.models import Brand, CarModel
from apps.core.models import BaseModel
from apps.core.services.upload_image import upload_listing_image
from apps.payment.models import CurrencyRate
from apps.users.models import Profile, User


class Region(models.Model):

    class Meta:
        db_table = 'region'
        ordering = ["id"]

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.name


def validate_max_year(value):
    current_year = timezone.now().year
    if value > current_year + 1:
        raise ValidationError(f"Рік випуску не може бути більшим за {current_year + 1}.")


class Listing(BaseModel):

    class Meta:
        db_table = 'listing'
        ordering = ['id']
        indexes = [
            models.Index(fields=['price_usd'], name='listing_price_usd_idx'),
            models.Index(fields=['price_eur'], name='listing_price_eur_idx'),
            models.Index(fields=['price_uah'], name='listing_price_uah_idx'),
            models.Index(fields=['year'], name='listing_year_idx'),
            models.Index(fields=['status'], name='listing_status_idx'),
        ]

    class CarConditions(models.TextChoices):
        NEW = 'new', 'Новий'
        USED = 'used', 'Вживаний'

    class BodyType(models.TextChoices):
        SEDAN = 'sedan', 'Седан'
        SUV = 'suv', 'Позашляховик'
        HATCHBACK = 'hatchback', 'Хетчбек'
        COUPE = 'coupe', 'Купе'
        WAGON = 'wagon', 'Універсал'
        PICKUP = 'pickup', 'Пікап'
        VAN = 'van', 'Мінівен'
        CABRIO = 'cabrio', 'Кабріолет'

    class FuelType(models.TextChoices):
        PETROL = 'petrol', 'Бензин'
        DIESEL = 'diesel', 'Дизель'
        HYBRID = 'hybrid', 'Гібрид'
        ELECTRIC = 'electric', 'Електричний'
        GAS = 'gas', 'Газ'

    class TransmissionType(models.TextChoices):
        MANUAL = 'manual', 'Механіка'
        AUTOMATIC = 'automatic', 'Автомат'
        ROBOT = 'robot', 'Робот'
        CVT = 'cvt', 'Варіатор'

    class DriveType(models.TextChoices):
        FWD = 'fwd', 'Передній привід'
        RWD = 'rwd', 'Задній привід'
        AWD = 'awd', 'Повний привід'

    class CurrencyType(models.TextChoices):
        USD = 'USD', 'Долар США'
        EUR = 'EUR', 'Євро'
        UAH = 'UAH', 'Гривня'

    class ListingStatus(models.TextChoices):
        ACTIVE = 'active', 'Активне'
        PENDING = 'pending', 'На перевірці'
        REJECTED = 'rejected', 'Відхилено'
        BLOCKED = 'blocked', 'Заблоковано'
        INACTIVE = 'inactive', 'Знято з продажу продавцем'

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="listings"
    )

    car_model = models.ForeignKey(
        CarModel,
        on_delete=models.CASCADE,
        related_name="listings"
    )

    color = models.CharField(max_length=50)
    region = models.ForeignKey(Region, on_delete=models.PROTECT, related_name="listings")

    year = models.PositiveIntegerField(
        validators=[MinValueValidator(1900), validate_max_year]
    )
    mileage = models.PositiveIntegerField(help_text='Пробіг у кілометрах')
    engine_volume = models.DecimalField(max_digits=4, decimal_places=1)

    condition_type = models.CharField(max_length=20, choices=CarConditions)
    body_type = models.CharField(max_length=20, choices=BodyType)
    fuel_type = models.CharField(max_length=20, choices=FuelType)
    transmission_type = models.CharField(max_length=20, choices=TransmissionType)
    drive_type = models.CharField(max_length=20, choices=DriveType)
    description = models.TextField(blank=True)

    currency = models.CharField(max_length=10, choices=CurrencyType)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    price_usd = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_eur = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_uah = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    exchange_rate = models.ForeignKey(
        CurrencyRate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    status = models.CharField(max_length=10, choices=ListingStatus, default=ListingStatus.PENDING)

    edit_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.car_model.brand} {self.car_model} {self.year}"


class CarImage(models.Model):

    class Meta:
        db_table = 'car_images'
        ordering = ['id']

    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="car_images")
    image = models.ImageField(upload_to=upload_listing_image)
    is_main = models.BooleanField(default=False)  # Головне фото оголошення