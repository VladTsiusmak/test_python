from django.urls import path

from apps.users.views import UserListView, UserMeView, UserMeUpdateView, UserMeDeleteView, UserToPremiumView, \
    UserDetailView, UserDeleteView, UserBlockView, UserUnblockView, UserToManagerView

urlpatterns = [
    path('', UserListView.as_view()),
    path('me/', UserMeView.as_view()),
    path('me/update/', UserMeUpdateView.as_view()),
    path('me/delete/', UserMeDeleteView.as_view()),
    path('me/premium/mock/', UserToPremiumView.as_view()),
    path('<int:pk>/', UserDetailView.as_view()),
    path('<int:pk>/delete/', UserDeleteView.as_view()),
    path('<int:pk>/block/', UserBlockView.as_view()),
    path('<int:pk>/unblock/', UserUnblockView.as_view()),
    path('<int:pk>/manager/', UserToManagerView.as_view()),
]