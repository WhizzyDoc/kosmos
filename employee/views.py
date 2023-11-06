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
from admins.models import *
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

class BankAccountCreateView(CreateAPIView):
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

class BankAccountRetrieveUpdateViewDeleteView(RetrieveUpdateDestroyAPIView):
    queryset = Bank.objects.all()
    serializer_class = BankAccountSerializer
    permission_classes = [AllowAny]

    def get(self, request, api_token, *args, **kwargs):
        # Get the user's primary key based on the provided API token
        user_profile = Profile.objects.get(api_token=api_token)
        user_pk = user_profile.pk
        # Retrieve all bank accounts for this user
        bank_account = BankAccount.objects.get(user=user_pk)

        serializer = self.serializer_class(bank_account)
        # if serializer.is_valid():
        return Response(
            serializer.data, status = status.HTTP_200_OK
        )

    def update(self, request,api_token, *args, **kwargs):
        user_profile = Profile.objects.get(api_token=api_token)
        user_pk = user_profile.pk
        bank_account = BankAccount.objects.get(user=user_pk)
        data = request.data.copy()

        data["user"] = user_pk

        bank_name = request.data["bank"]
        try:
            bank = Bank.objects.get(bank_name=bank_name)
            bank_pk = bank.pk
        except:
            bank_pk = None
        data["bank"] = bank_pk
        serializer = self.serializer_class(bank_account, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data, status = status.HTTP_200_OK
                )
        else:
            return Response(
                serializer.errors,
                status = status.HTTP_400_BAD_REQUEST
                )

    def destroy(self, request,api_token, *args, **kwargs):

        try:
            user_profile = Profile.objects.get(api_token=api_token)
            user_pk = user_profile.pk
            bank_account = BankAccount.objects.get(user=user_pk)
            bank_account.delete()

            return Response({
                "Success": "You've successfully deleted your bank account details"
            }, status = status.HTTP_200_OK)
        except:
            return Response({
                "Error": "Sorry, an error occured!"
            }, status = status.HTTP_400_BAD_REQUEST)

        

        



from .filters import ProfileFilter
from django_filters.rest_framework import DjangoFilterBackend

class EmployeeListView(ListCreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]
    name = 'employees'
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProfileFilter



class CreateListEventView(ListCreateAPIView, UpdateAPIView, DestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [AllowAny]


    def get(self, request,pk, *args, **kwargs):
        # api_token = pk
        type_ = self.request.query_params.get('type')
        print(pk)
        user = Profile.objects.get(api_token=pk)
        if user.is_premium_user:
            events =  Event.objects.all()
        if type_ == "open":
            events =  Event.objects.filter(invitees=user, type = "open")
        elif type_ == "invitation":
            events = Event.objects.filter(invitees = user, type = "invitation")
        else:
            events = Event.objects.filter(invitees = user)

        serializer = EventSerializer(events, many=True)

        return Response(serializer.data)

    def create(self, request, pk, *args, **kwargs):
        user_profile = Profile.objects.get(api_token = pk)
        user_pk = user_profile.pk
        if user_profile.is_premium_user:
            data = request.data.copy()
            data["organizer"] = user_pk
            data["attending"] = []
            serializer = self.serializer_class(data = data)
            # print(serializer.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({
                "Error": "You cant perform this action"
            }, status=status.HTTP_401_UNAUTHORIZED)

class RetrieveUpdateDestroyEventView(RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [AllowAny]
    lookup_field = "id"

    def update(self, request, api_token, id, *args, **kwargs):

        event = Event.objects.get(id = id)
        user_profile = Profile.objects.get(api_token = api_token)
        user_pk = user_profile.pk

        if user_profile.is_premium_user:
            data = request.data.copy()
            data["organizer"] = user_pk
            data["attending"] = event.attending
            serializer = self.serializer_class(data = data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status = status.HTTP_200_OK)
            else:
                return Response(serializer.error, status = status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "Error": "Can't perform this action"
            }, status=status.HTTP_401_UNAUTHORIZED)



    def destroy(self, request, api_token, id, *args, **kwargs):
        user_profile = Profile.objects.get(api_token = api_token)
        user_pk = user_profile.pk

        if user_profile.is_premium_user:
            event = get_object_or_404(Event, id=id)
            event.delete()
            return Response({
                "Deleted": "You've deleted this event"
            }, status = status.HTTP_200_OK)
        else:
            return Response({
                "Error": "You can't perform that action"
            }, status = status.HTTP_401_UNAUTHORIZED)

class AttendingEventView(UpdateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [AllowAny]
    lookup_field = "id"

    def update(self, request,api_token,id, *args, **kwargs):
        try:
            event = Event.objects.get(id = id)
            user_profile = Profile.objects.get(api_token = api_token)
            user_pk = user_profile.pk

            if event.invitees.filter(pk=user_pk).exists():
                event.attending.add(user_profile)
                event.save()
                return Response({
                    "Saved": "You successfully accepted the invite"
                }, status=status.HTTP_200_OK)

        except:
            return Response({
                "Error": "An error occured"
            }, status = status.HTTP_400_BAD_REQUEST)