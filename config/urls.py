from django.contrib import admin
from django.urls import include, path

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path("api/auth/", include('apps.auth.urls')),
    path("api/users/", include('apps.users.urls')),
    path("api/cars/", include('apps.cars.urls')),
    path("api/listings/", include('apps.listing.urls')),
    path('api/listings/statistics/', include('apps.listing_stats.urls')),
    path('api/payment/', include('apps.payment.urls')),
]