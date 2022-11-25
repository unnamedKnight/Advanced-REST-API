from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    path('create-user', views.CreateUserView.as_view(), name='create_user'),
    # path('login', views.CreateTokenView.as_view(), name='login'),
    path('login', obtain_auth_token, name='login'),
    path('logout', views.logout_user, name='logout'),
]