from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from rest_framework.generics import GenericAPIView, RetrieveUpdateDestroyAPIView, ListCreateAPIView, CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.mixins import CreateModelMixin
from main.models import Profile, BankAccount, Bank
from admins.views import generate_token
from .serializers import *
# Create your views here.

class LoginView(GenericAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        try:
            user = get_object_or_404(User, username = request.data["username"])

            if not user.check_password(request.data["password"]):
                return Response({
                    "detail": "not found"
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                user_profile = Profile.objects.get(user = user)
                if user_profile.api_token:
                    token = user_profile.api_token
                else:
                    # generate token
                    token = generate_token()
                    user_profile.api_token = token
                    user_profile.save()

                return Response({
                    "status": "success",
                    "message": "Login successful",
                    "data": ProfileSerializer(user_profile).data
            }, status = status.HTTP_200_OK)

        except:
            return Response({
                "Error": "Can't complete this action"
            }, status= status.HTTP_400_BAD_REQUEST)

# Read, Update and Delete
class ProfileView(RetrieveUpdateDestroyAPIView):
    queryset = Profile.objects.all()
    permission_classes = [AllowAny]
    lookup_field = "api_token"
    parser_classes = [FormParser, MultiPartParser, JSONParser]
    serializer_class = ProfileSerializer

    def update(self, request, *args, **kwargs):
        response =  super().update(request, *args, **kwargs)

        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            image = request.data.get("image", None)
            if image:
                instance.image = image
            serializer.save()

            return Response(serializer.data)

        else: return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Create Bank Account 

class BankAccountView(CreateAPIView):
    queryset = Bank.objects.all()
    lookup_field = "api_token"
    serializer_class = BankAccountSerializer
    permission_classes = [AllowAny]


    def create(self, request, api_token, *args, **kwargs):
        # Get the user's primary key based on the provided API token
        user = Profile.objects.get(api_token=api_token)
        user_pk = user.pk

        # Get the bank's primary key based on the provided bank name
        bank_name = request.data["bank"]
        try:
            bank = Bank.objects.get(bank_name=bank_name)
            bank_pk = bank.pk
        except:
            bank_pk = None

        # Create a copy of request.data and set user and bank primary keys
        data = request.data.copy()
        data["user"] = user_pk
        data["bank"] = bank_pk
        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            if BankAccount.objects.filter(user = user_pk).exists():
                return Response({"error": "You already have a bank account", "user": serializer.data}, status=status.HTTP_409_CONFLICT)
        
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from .filters import ProfileFilter
from django_filters.rest_framework import DjangoFilterBackend

class EmployeeListView(ListCreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]
    name = 'employees'
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProfileFilter