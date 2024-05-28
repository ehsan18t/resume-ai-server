from django.urls import path, re_path

from .views import *

urlpatterns = [
    re_path(
        r'^o/(?P<provider>\S+)/$',
        CustomProviderAuthView.as_view(),
        name='provider-auth'
    ),
    path('jwt/create/', CustomTokenObtainPairView.as_view()),
    path('jwt/refresh/', CustomTokenRefreshView.as_view()),
    path('jwt/verify/', CustomTokenVerifyView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('user/', get_user_by_id, name='get-user-by-id'),
    path('pdftoprofile/', pdf_to_profile, name='pdf-to-profile'),
    path('profile/', get_profile_by_id, name='get-profile'),
]
