from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register('site', views.SiteViewSet)
router.register('profile', views.ProfileViewSet)
router.register('departments', views.DepartmentViewSet)
router.register('positions', views.PositionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]