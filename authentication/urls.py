from django.urls import path
from .views import UserView, RegisterView, LoginView, LogoutView, ToggleFavoriteView, SellerProfileView, UsernameView, FavoritesListView

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

    path('user/seller/<int:seller_id>/', UsernameView.as_view()),
    path('user/seller/<int:seller_id>/profile/', SellerProfileView.as_view()),
]

