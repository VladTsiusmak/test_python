from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    GenericAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    get_object_or_404,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema

from apps.core.permissions.permissions import HasPermissionCodename, IsImageOwner, IsOwner
from apps.listing.filters import ListingFilter
from apps.listing.models import CarImage, Listing, Region
from apps.listing.my_listing_filter import MyListingFilter
from apps.listing.serializers import (
    ImageSerializer,
    ImageUploadSerializer,
    ListingModerationSerializer,
    ListingReadSerializer,
    ListingWriteSerializer,
    RegionSerializer,
    SendReportSerializer,
)
from apps.listing.tasks import send_blocked_listing_email_task, send_report_email_task, update_one_listing_prices_task
from apps.listing_stats.models import ListingStats
from apps.moderation.tasks import moderation_listings_task


@extend_schema(
    summary="Список всіх активних оголошень",
    description="Доступно всім"
)
class ListingsListView(ListAPIView):

    queryset = (
        Listing.objects.filter(status='active')
        .select_related(
            'owner',
            'car_model',
            'car_model__brand',
            'region',
            'exchange_rate'
        )
        .prefetch_related('car_images')
    )
    serializer_class = ListingReadSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering_fields = [
        "created_at",
        "price_uah",
        "price_usd",
        "price_eur",
        "year",
    ]
    ordering = ["-created_at"]
    filterset_class = ListingFilter
    search_fields = [
        'description',
        'color',
        'car_model__name',
        'car_model__brand__name'
    ]


@extend_schema(
    summary="Переглянути одне оголошення",
    description="Дозволяє переглядати конкретне оголошення по ID. Доступно всім"
)
class ListingView(RetrieveAPIView):

    queryset = (
        Listing.objects.filter(status='active')
        .select_related(
            'owner',
            'car_model',
            'car_model__brand',
            'region',
            'exchange_rate'
        )
        .prefetch_related('car_images')
    )
    serializer_class = ListingReadSerializer

    def retrieve(self, request, *args, **kwargs):
        listing = self.get_object()
        if not request.user.is_authenticated or request.user != listing.owner:
            ListingStats.objects.create(
                listing=listing,
                viewer=request.user if request.user.is_authenticated else None
            )

        serializer = self.get_serializer(listing)
        return Response(serializer.data)


@extend_schema(
    summary="Список регіонів",
    description="Доступно для всіх користувачів"
)
class RegionsListView(ListAPIView):

    queryset = Region.objects.all()
    serializer_class = RegionSerializer



@extend_schema(
    summary="Список власних оголошень",
    description="Доступно лише для власників"
)
class MyListingsListView(ListAPIView):

    serializer_class = ListingReadSerializer
    permission_classes = [HasPermissionCodename]
    required_permission = 'can_view_own_listings'
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MyListingFilter
    search_fields = [
        "description",
        "car_model__name",
        "car_model__brand__name",
    ]
    ordering_fields = [
        "created_at",
        "price_uah",
        "price_usd",
        "price_eur",
        "year",
    ]
    ordering = ["-created_at"]

    def get_queryset(self):
        return (
            Listing.objects.filter(owner=self.request.user)
            .select_related(
                "owner",
                "car_model",
                "car_model__brand",
                "region",
                "exchange_rate",
            )
            .prefetch_related('car_images')
        )


@extend_schema(
    summary="Створити оголошення",
    description="Доступно для продавців і покупців. Покупці в момент створення оголошення змінюють роль і стають продавцями"
)
class ListingCreateView(CreateAPIView):

    queryset = Listing.objects.all()
    serializer_class = ListingWriteSerializer
    permission_classes = [HasPermissionCodename]
    required_permission = 'can_create_listing'

    def perform_create(self, serializer):
        listing = serializer.save()
        moderation_listings_task.delay(listing.id)
        update_one_listing_prices_task.delay(listing.id)


@extend_schema(
    summary="Оновити власне оголошення",
    description="Дозволяє вносити правки у власне оголошення"
)
class ListingUpdateView(UpdateAPIView):

    queryset = Listing.objects.filter(status__in=['active', 'rejected'])
    serializer_class = ListingWriteSerializer
    permission_classes = [HasPermissionCodename, IsOwner]
    required_permission = 'can_update_own_listing'
    http_method_names = ['patch']

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.edit_count >= 2 and instance.status == 'rejected':
            instance.status = 'inactive'
            instance.save(update_fields=['status'])
            send_blocked_listing_email_task.delay(instance.id)
            return Response(
                {'message': 'Listing has been blocked.',
                 'listing': self.get_serializer(instance).data},
                status=status.HTTP_200_OK
            )

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        if instance.status == 'rejected':
            updated = serializer.save(
                edit_count=instance.edit_count + 1,
                status='pending'
            )
        else:
            updated = serializer.save(status='pending')

        moderation_listings_task.delay(updated.id)
        return Response(
            {
                'message': 'Listing has been updated.',
                'listing': serializer.data
            },
            status=status.HTTP_200_OK
        )


@extend_schema(
    summary="Видалити власне оголошення",
    description="Дозволяє видаляти власне оголошення"
)
class ListingDeleteView(DestroyAPIView):

    queryset = Listing.objects.filter(status__in=['active', 'rejected', 'pending'])
    serializer_class = ListingWriteSerializer
    permission_classes = [HasPermissionCodename, IsOwner]
    required_permission = 'can_delete_own_listing'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = 'inactive'
        instance.save(update_fields=['status'])
        return Response(
            {'message': 'Listing has been deactivated.',
             'listing': self.get_serializer(instance).data},
            status=status.HTTP_200_OK
        )


@extend_schema(
    summary="Завантаження фото",
    description="Дозволяє завантажити одне або кілька фото у власне оголошення"
)
class ImagesUploadView(CreateAPIView):

    queryset = Listing.objects.all()
    serializer_class = ImageUploadSerializer
    permission_classes = [HasPermissionCodename, IsOwner]
    required_permission = 'can_upload_own_images'

    def perform_create(self, serializer):
        self.check_object_permissions(self.request, self.get_object())
        serializer.save()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['listing_id'] = self.kwargs['pk']
        return context

    def create(self, request, *args, **kwargs):
        self.check_object_permissions(request, self.get_object())
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        images = serializer.save()
        return Response(
            {
                'message': 'Images uploaded successfully.',
                'images': ImageSerializer(images, many=True).data
            },
            status=status.HTTP_201_CREATED
        )


@extend_schema(
    summary="Видалити фото",
    description="Дозволяє видалити фото по ID з власного оголошення. Треба вказати ID фотографії"
)
class ImageDeleteView(DestroyAPIView):

    queryset = CarImage.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [HasPermissionCodename, IsImageOwner]
    required_permission = 'can_delete_own_images'

    def destroy(self, request, *args, **kwargs):
        photo = self.get_object()
        photo.delete()
        return Response(
            {'message': 'Image has been deleted.'},
            status=status.HTTP_200_OK
        )


@extend_schema(
    summary="Список оголошень для модерації",
    description="Дозволяє переглянути список оголошень зі статусом pending для їх модерації. Доступно менеджерам і адміністраторам"
)
class PendingListingsListView(ListAPIView):

    queryset = (
        Listing.objects.filter(status='pending')
        .select_related(
            'owner',
            'car_model',
            'car_model__brand',
            'region',
            'exchange_rate'
        )
        .prefetch_related('car_images')
    )
    serializer_class = ListingReadSerializer
    permission_classes = [HasPermissionCodename]
    required_permission = 'can_edit_listings'


@extend_schema(
    summary="Модерація оголошення",
    description="Модерація оголошення менеджером або адміністратором. Оголошення отримує статус active, якщо проходе первірку, rejected - відхилено, "
                "blocked - якщо заблоковане"
)
class ModeratingListingView(UpdateAPIView):

    queryset = Listing.objects.filter(status='pending')
    serializer_class = ListingModerationSerializer
    permission_classes = [HasPermissionCodename]
    required_permission = 'can_moderate_listings'
    http_method_names = ['patch']

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'message': 'Listing has been moderated.',
             'listing': serializer.data},
            status=status.HTTP_200_OK
        )


@extend_schema(
    summary="Повідомити про проблему",
    description="Відправка email адміністрації з повідомленням про проблему з оголошенням по ID чи продавцем. Доступно залогіненим користувачам"
)
class ReportAboutProblemView(GenericAPIView):
    serializer_class = SendReportSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        listing = get_object_or_404(Listing, pk=self.kwargs['pk'])
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        send_report_email_task.delay(listing.id, request.user.id, serializer.validated_data['message'])
        return Response(
            {'message': 'Problem has been sent.'},
            status=status.HTTP_200_OK
        )