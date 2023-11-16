from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
#router.register('users', views.ProfileViewSet)

urlpatterns = [
    path("login", views.LoginView.as_view(), name = "login"),
    path("profile/<str:api_token>", views.ProfileView.as_view(), name = "profile"),
    path("bank/<str:api_token>", views.BankAccountCreateView.as_view(), name = "bank"),
    path("bank-profile/<str:api_token>", views.BankAccountRetrieveUpdateViewDeleteView.as_view(), name="bank-profile"),
    path("employees", views.EmployeeListView.as_view(), name = "employees"),
    path("events/<str:pk>", views.CreateListEventView.as_view(), name = "events"),
    path("event/<str:api_token>/<str:id>", views.RetrieveUpdateDestroyEventView.as_view(), name="event"),
    path("complaint/<str:api_token>", views.ComplaintView.as_view(), name = "complaint"),
    path("complaint/action/<str:api_token>/<str:id>", views.RetrieveUpdateDeleteComplaintView.as_view(), name = "get-complaint"),
    path("news/<str:api_token>", views.NewsView.as_view(), name = "news"),
    path("news/<str:api_token>/<str:id>", views.RetrieveNewsView.as_view(), name = "read-news"),
    path("groups/<str:api_token>", views.GroupChats.as_view(), name = "groups"),
    path("group/<str:api_token>/<str:id>", views.GroupChatDetailsView.as_view(), name = "group-chat"),
    path("chat/<api_token>/<str:pk>", views.ChatMessageCreateView.as_view(), name = "chat"),
    path("query/<str:api_token>", views.QueryView.as_view(), name = "query"),
    path("activities/<str:api_token>", views.LogView.as_view(), name = "activities"),
    path("notifications/<str:api_token>", views.NotificationsView.as_view(), name = "notifications"),
    path("changepassword", views.ChangePassword.as_view(), name = "change-password"),
    path("forgotpassword_getnew", views.ForgotPassword_GetNewPasswordView.as_view(), name = "forgotpassword-getnew"),
    path("forgotpassword_reset", views.ResetPassword.as_view(), name = "reset-password"),
    path("tasks/<str:api_token>", views.TaskView.as_view(), name = "tasks"),
    
]
