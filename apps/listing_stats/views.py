from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response

from apps.core.permissions.permissions import HasPermissionCodename, IsOwner
from apps.listing.models import Listing
from apps.listing_stats.serializers import ListingStatsSerializer
from apps.listing_stats.services import ListingStatsService
from apps.users.models import Role, Profile


@extend_schema(
    summary='Переглянути статистику',
    description='Дозволяє преміум-користувачам отримувати статистику по власним оголошенням. Інформація доступна менеджерам і адміністраторам',
)
class ListingStatsView(RetrieveAPIView):
    queryset = Listing.objects.all()
    serializer_class = ListingStatsSerializer
    permission_classes = [HasPermissionCodename, IsOwner]
    required_permission = 'can_view_statistics'

    def retrieve(self, request, *args, **kwargs):
        listing = self.get_object()
        if not request.user.is_superuser and (not request.user.role or request.user.role.name != Role.RoleName.MANAGER):
            if not request.user.profile or request.user.profile.account_type != Profile.AccountType.PREMIUM:
                return Response(
                    {'message': 'Premium account required'},
                    status=status.HTTP_403_FORBIDDEN
                )
        stats = ListingStatsService.get_stats(listing)
        serializer =self.get_serializer(stats)
        return Response(serializer.data)