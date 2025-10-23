from django.urls import path
from .views import RegisterView, LoginView, UserListView, UserView, LogoutView, ToggleFavoriteView, FavoritesListView, BuyerShippingView

urlpatterns = [
    # Auth endpoints
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('user/', UserView.as_view()),

    # User profile endpoints
    path('', UserListView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('user/favorites/toggle/', ToggleFavoriteView.as_view(),
         name='toggle_favorite'),
    path('user/favorites/', FavoritesListView.as_view(), name='favorites_list'),
    path('user/items/<int:item_id>/shipping/',
         BuyerShippingView.as_view(), name='shipping'),


    # These endpoints would need corresponding views to be implemented
    # path('password/reset/', PasswordResetView.as_view()),
    # path('password/reset/confirm/<str:token>/', PasswordResetConfirmView.as_view()),
    # path('email/verify/<str:token>/', EmailVerificationView.as_view()),
    # path('payment-methods/', PaymentMethodListView.as_view()),
    # path('payment-methods/<int:pk>/', PaymentMethodDetailView.as_view()),

    # Account settings
    # path('settings/notifications/', NotificationSettingsView.as_view()),
]
