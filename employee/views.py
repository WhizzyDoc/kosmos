from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from rest_framework.generics import GenericAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.mixins import CreateModelMixin
from main.models import Profile
from admins.views import generate_token
from .serializers import ProfileSerializer
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
                    "User Details": request.data,
                    "api_token": token
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


# CRUD

class BankView(CreateModelMixin, RetrieveUpdateDestroyAPIView):
    pass