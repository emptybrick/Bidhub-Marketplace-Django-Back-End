from django.urls import path
from .views import RegisterView, LoginView

urlpatterns = [
    # Auth endpoints
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),

    # User profile endpoints
    # path('users/<int:pk>/account/', UserView.as_view()),





    # path('profile/update/', ProfileUpdateView.as_view()),

    # These endpoints would need corresponding views to be implemented
    # path('password/reset/', PasswordResetView.as_view()),
    # path('password/reset/confirm/<str:token>/', PasswordResetConfirmView.as_view()),
    # path('email/verify/<str:token>/', EmailVerificationView.as_view()),

    # User addresses and payment methods
    # path('addresses/', AddressListView.as_view()),
    # path('addresses/<int:pk>/', AddressDetailView.as_view()),
    # path('payment-methods/', PaymentMethodListView.as_view()),
    # path('payment-methods/<int:pk>/', PaymentMethodDetailView.as_view()),

    # User activity and metrics
    # path('dashboard/', UserDashboardView.as_view()),
    # path('users/<int:pk>/ratings/', UserRatingsView.as_view()),
    # path('users/<int:pk>/seller-metrics/', SellerMetricsView.as_view()),

    # Account settings
    # path('settings/notifications/', NotificationSettingsView.as_view()),
    # path('settings/privacy/', PrivacySettingsView.as_view()),
]
