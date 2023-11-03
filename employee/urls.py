from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
#router.register('users', views.ProfileViewSet)

urlpatterns = [
    # path('', include(router.urls)),
    path("login", views.LoginView.as_view(), name = "login"),
    path("profile/<str:api_token>", views.ProfileView.as_view(), name = "profile")
]