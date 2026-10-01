from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import (
    GenericAPIView,
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    get_object_or_404,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.cars.models import Brand, CarModel
from apps.cars.serializers import BrandSerializer, CarModelReadSerializer, CarModelWriteSerializer, SendEmailSerializer
from apps.cars.tasks import send_offer_new_carmodel_task
from apps.core.permissions.permissions import HasPermissionCodenameOrReadOnly

# ===================== МОДЕЛІ АВТОМОБІЛІВ =====================

@extend_schema_view(
    get=extend_schema(
        summary="Список моделей авто",
        description="Доступно всім користувачам"
    ),
    post=extend_schema(
        summary="Додати нову модель авто",
        description="Доступно менеджерам і адміністраторам",
    )
)
class CarModelListCreateView(ListCreateAPIView):
    """Список та створення моделей автомобілів."""

    queryset = CarModel.objects.select_related("brand")
    permission_classes = [HasPermissionCodenameOrReadOnly]
    required_permission = 'can_add_car_models'

    filter_backends = [OrderingFilter, SearchFilter]
    search_fields = ["name", "brand__name"]
    ordering_fields = ["name"]
    ordering = ["name"]

    def get_serializer_class(self):
        # Для читання - з вкладеним брендом, для запису - тільки ID
        if self.request.method == 'GET':
            return CarModelReadSerializer
        return CarModelWriteSerializer


@extend_schema_view(
    get=extend_schema(
        summary="Отримати інформацію про модель авто",
        description="Доступно всім користувачам"
    ),
    delete=extend_schema(
        summary="Видалити модель авто",
        description="Видаляє модель авто по ID, дозволено лише адміністратору"
    ),
    patch=extend_schema(
        summary="Оновити інформацію про модель авто",
        description="Оновлення/виправлення інформації про модель авто по ID, дозволено лише адміністратору"
    )
)
class CarModelDetailView(RetrieveUpdateDestroyAPIView):
    """Детальний перегляд, оновлення та видалення моделі авто."""

    queryset = CarModel.objects.select_related("brand")
    permission_classes = [HasPermissionCodenameOrReadOnly]
    required_permission = 'can_update_delete_car_models'
    http_method_names = ['get', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CarModelReadSerializer
        return CarModelWriteSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {'message': 'CarModel has been deleted.'},
            status=status.HTTP_200_OK
        )


# ===================== БРЕНДИ АВТОМОБІЛІВ =====================

@extend_schema_view(
    get=extend_schema(
        summary="Список брендів",
        description="Доступно всім користувачам"
    ),
    post=extend_schema(
        summary="Додати новий бренд",
        description="Доступно менеджерам і адміністраторам",
    )
)
class BrandListCreateView(ListCreateAPIView):
    """Список та створення брендів автомобілів."""

    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [HasPermissionCodenameOrReadOnly]
    required_permission = 'can_add_brands'

    filter_backends = [OrderingFilter, SearchFilter]
    search_fields = ["name"]
    ordering_fields = ["name"]
    ordering = ["name"]


@extend_schema_view(
    get=extend_schema(
        summary="Отримати інформацію про бренд",
        description="Доступно всім користувачам"
    ),
    delete=extend_schema(
        summary="Видалити бренд",
        description="Видаляє бренд по ID, дозволено лише адміністратору"
    ),
    patch=extend_schema(
        summary="Оновити інформацію про бренд",
        description="Оновлення/виправлення інформації про бренд по ID, дозволено лише адміністратору"
    )
)
class BrandDetailView(RetrieveUpdateDestroyAPIView):
    """Детальний перегляд, оновлення та видалення бренду."""

    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [HasPermissionCodenameOrReadOnly]
    required_permission = 'can_update_delete_brands'
    http_method_names = ['get', 'patch', 'delete']

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {'message': 'Brand has been deleted.'},
            status=status.HTTP_200_OK
        )


# ===================== ДОДАТКОВІ ЕНДПОІНТИ =====================

@extend_schema(
    summary="Отримати список автомобілів конкретного бренду",
    description="Доступно всім користувачам"
)
class CarModelByBrandView(ListAPIView):
    """Список моделей за ID бренду."""

    serializer_class = CarModelReadSerializer

    def get_queryset(self):
        # Перевіряємо, чи існує бренд
        get_object_or_404(Brand, pk=self.kwargs["pk"])
        return (
            CarModel.objects
            .filter(brand_id=self.kwargs["pk"])
            .select_related("brand")
        )


@extend_schema(
    summary="Відправити запит на додавання нового бренду чи моделі",
    description="Відправка email адміністрації, доступно залогіненим користувачам"
)
class OfferNewCarModelView(GenericAPIView):
    """Відправка пропозиції щодо нової моделі або бренду."""

    serializer_class = SendEmailSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        send_offer_new_carmodel_task.delay(request.user.id, serializer.validated_data['message'])
        return Response(
            {'message': 'Your request has been sent.'},
            status=status.HTTP_200_OK
        )