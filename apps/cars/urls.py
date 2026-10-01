from django.urls import path

from apps.cars.views import BrandListCreateView, BrandDetailView, CarModelListCreateView, CarModelDetailView, \
    CarModelByBrandView, OfferNewCarModelView

urlpatterns = [
    path('brands/', BrandListCreateView.as_view(), name='brand-list-create'),
    path('brands/<int:pk>/', BrandDetailView.as_view(), name='brand-detail'),
    path('models/', CarModelListCreateView.as_view(), name='carmodel-list-create'),
    path('models/<int:pk>/', CarModelDetailView.as_view(), name='carmodel-detail'),
    path('brands/<int:pk>/models/', CarModelByBrandView.as_view(), name='brand-models-list-create'),
    path('request-barnd/', OfferNewCarModelView.as_view(), name='offer-new-car-model'),
]