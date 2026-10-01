from django.urls import path

from apps.listing.views import (
    ImageDeleteView,
    ImagesUploadView,
    ListingCreateView,
    ListingDeleteView,
    ListingsListView,
    ListingUpdateView,
    ListingView,
    ModeratingListingView,
    MyListingsListView,
    PendingListingsListView,
    RegionsListView,
    ReportAboutProblemView,
)

urlpatterns = [
    path('', ListingsListView.as_view(), name='listing-list'),
    path('<int:pk>/', ListingView.as_view(), name='listing-detail'),
    path('regions/', RegionsListView.as_view(), name='region-list'),

    path('my/', MyListingsListView.as_view(), name='my-listing-list'),
    path('create/', ListingCreateView.as_view(), name='listing-create'),
    path('update/<int:pk>/', ListingUpdateView.as_view(), name='listing-update'),
    path('delete/<int:pk>/', ListingDeleteView.as_view(), name='listing-delete'),
    path('<int:pk>/photos/', ImagesUploadView.as_view(), name='upload-photos'),
    path('photos/<int:pk>/', ImageDeleteView.as_view(), name='delete-photos'),

    path('edit/', PendingListingsListView.as_view(), name='edit-listings'),
    path('moderation/<int:pk>/', ModeratingListingView.as_view(), name='moderation-listing'),
    path('report-problem/<int:pk>/', ReportAboutProblemView.as_view(), name='report-about-problem'),
]