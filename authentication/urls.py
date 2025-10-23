from django.urls import path
from .views import UserView, RegisterView, LoginView, LogoutView, BuyerShippingView, ToggleFavoriteView, SellerProfileView, UsernameView, FavoritesListView

urlpatterns = [
    # Auth endpoints
    path('user/', UserView.as_view()),
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),

    # User profile endpoints
    path('user/favorites/toggle/', ToggleFavoriteView.as_view(),
         name='toggle_favorite'),
    path('user/favorites/', FavoritesListView.as_view(), name='favorites_list'),
    path('user/items/<int:item_id>/shipping/',
         BuyerShippingView.as_view()),
    path('user/seller/<int:seller_id>/', UsernameView.as_view()),
    path('user/seller/<int:seller_id>/profile/', SellerProfileView.as_view()),
]

# path('', UserListView.as_view()),
# These endpoints would need corresponding views to be implemented
# path('password/reset/', PasswordResetView.as_view()),
# path('password/reset/confirm/<str:token>/', PasswordResetConfirmView.as_view()),
# path('email/verify/<str:token>/', EmailVerificationView.as_view()),
# path('payment-methods/', PaymentMethodListView.as_view()),
# path('payment-methods/<int:pk>/', PaymentMethodDetailView.as_view()),

# Account settings
# path('settings/notifications/', NotificationSettingsView.as_view()),
