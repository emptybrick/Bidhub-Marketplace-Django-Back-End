from django.urls import path
from .views import RegisterView, LoginView, UserView, ProfileUpdateView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('users/<int:pk>/account/', UserView.as_view()), # or users/ or users/int:<pk>
]

# users/:userId/account