from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register('site', views.SiteViewSet)
router.register('profile', views.ProfileViewSet)
router.register('departments', views.DepartmentViewSet)
router.register('positions', views.PositionViewSet)
router.register('banks', views.BankViewSet)
router.register('news_categories', views.NewsCategoryViewSet)
router.register('news', views.NewsViewSet)
router.register('employees', views.EmployeeViewSet)
router.register('meetings', views.MeetingViewSet)
router.register('events', views.EventViewSet)
router.register('bank_accounts', views.BankAccountViewSet)
router.register('tasks', views.TaskViewSet)
router.register('complaints', views.ComplaintViewSet)
router.register('queries', views.QueryViewSet)
router.register('logs', views.LogViewSet)
router.register('notifications', views.NotificationViewSet)
router.register('rewards', views.RewardViewSet)
router.register('group_chats', views.GroupChatViewSet)

urlpatterns = [
    path('', include(router.urls)),
]