from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from rest_framework.generics import GenericAPIView, RetrieveUpdateDestroyAPIView, ListCreateAPIView, CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.mixins import CreateModelMixin
from main.models import Profile, BankAccount, Bank, Complaint
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

        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            image = request.data.get("image", None)
            if image:
                instance.image = image
            serializer.save()

            return Response(serializer.data)

        else: 
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Create Bank Account 

class BankAccountCreateView(CreateAPIView):
    queryset = Bank.objects.all()
    lookup_field = "api_token"
    serializer_class = BankAccountSerializer
    permission_classes = [AllowAny]


    def create(self, request, api_token, *args, **kwargs):
        # Get the user's primary key based on the provided API token
        try:
            user = Profile.objects.get(api_token=api_token)
            user_pk = user.pk
        except:
            return Response({
                "Error": "Can't find user"
            },status = status.HTTP_404_NOT_FOUND)

        # Get the bank's primary key based on the provided bank name
        bank_name = request.data["bank"].lower()
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
        try:
            user = Profile.objects.get(api_token=api_token)
            user_pk = user.pk
        except:
            return Response({
                "Error": "Can't find user"
                },status = status.HTTP_404_NOT_FOUND)

        # Retrieve all bank accounts for this user
        bank_account = BankAccount.objects.get(user=user_pk)

        serializer = self.serializer_class(bank_account)
        # if serializer.is_valid():
        return Response(
            serializer.data, status = status.HTTP_200_OK
        )

    def update(self, request,api_token, *args, **kwargs):
        try:
            user = Profile.objects.get(api_token=api_token)
            user_pk = user.pk
        except:
            return Response({
                "Error": "Can't find user"
                },status = status.HTTP_404_NOT_FOUND)
        bank_account = BankAccount.objects.get(user=user_pk)
        data = request.data.copy()

        data["user"] = user_pk

        if "bank" in request.data:
            bank_name = data["bank"].lower()
        else:
            bank_name = BankAccount.objects.get(user = user).bank.bank_name
        
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



class CreateListEventView(ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [AllowAny]


    def get(self, request,pk, *args, **kwargs):
        # api_token = pk
        try:
            user = Profile.objects.get(api_token=pk)
        except:
            return Response({
                "Error": "Cant complete your request"
            }, status = status.HTTP_400_BAD_REQUEST)

        return super(CreateListEventView, self).list(request, *args, **kwargs)

class RetrieveUpdateDestroyEventView(RetrieveAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [AllowAny]
    lookup_field = "id"

class ComplaintView(ListCreateAPIView):
    queryset = Complaint.objects.all()
    lookup_field = "api_token"
    serializer_class = ComplaintSerializer
    permission_classes = [AllowAny]

    def create(self, request, api_token, *args, **kwargs):
        profile = Profile.objects.get(api_token = api_token)
        user_pk = profile.pk

        data = request.data.copy()
        
        data["employee"] = user_pk

        serializer = self.serializer_class(data = data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    def get(self, request, api_token, *args, **kwargs):
        try:
            profile = Profile.objects.get(api_token = api_token)
            user_pk = profile.pk
        except:
            return Response({
                "Error": "Can't complete this action"
            }, status = status.HTTP_400_BAD_REQUEST)
        filter_by = self.request.query_params.get("by")
        if filter_by == "user":
            serializer = self.serializer_class(Complaint.objects.filter(employee = user_pk), many = True)
        else:
            serializer = self.serializer_class(Complaint.objects.all(), many = True)


        return Response(serializer.data)

class RetrieveUpdateDeleteComplaintView(RetrieveUpdateDestroyAPIView):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    lookup_url_kwarg = 'id'
    permission_classes = [AllowAny]

    def get(self, request, id, *args, **kwargs):
        complaint = self.get_object()
        serializer = self.serializer_class(complaint)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, api_token, id, *args, **kwargs):
        try:
            user_profile = Profile.objects.get(api_token=api_token)
        except Profile.DoesNotExist:
            return Response({"Error": "Invalid api_token"}, status=status.HTTP_401_UNAUTHORIZED)

        complaint = Complaint.objects.get(id=id)
        print(user_profile, complaint.employee)
        # Check if the user is the owner of the complaint or an admin
        if user_profile == complaint.employee:

            if 'title' in request.data or 'complaint' in request.data or 'proposed_solution' in request.data:
                data = request.data.copy()
                serializer = self.serializer_class(instance=complaint, data=data, partial=True)

                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({"Error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        # Allowing admin to edit solution and addressed fields
            elif 'solution' in request.data or 'addressed' in request.data:
                    return Response({"Error": "Cant add Solution to your own complaints"}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({"Error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)




    def destroy(self, request, api_token, id, *args, **kwargs):
        try:
            user_profile = Profile.objects.get(api_token=api_token)
        except Profile.DoesNotExist:
            return Response({"Error": "Invalid api_token"}, status=status.HTTP_401_UNAUTHORIZED)

        complaint = Complaint.objects.get(id=id)

        if user_profile.pk == complaint.employee:
            complaint.delete()
            return Response({"Message": "Complaint deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"Error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)


class NewsView(ListAPIView):
    queryset = News.objects.filter(active = True)
    serializer_class = NewsSerializer
    permission_classes = [AllowAny]

    def get(self, request, api_token, *args, **kwargs):
        try:
            user = Profile.objects.get(api_token = api_token)
        except:
            return Response({
                "Error": "Sorry, an error occured"
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(News.objects.filter(active = True), many = True )

        return Response(serializer.data, status = status.HTTP_200_OK)

class RetrieveNewsView(RetrieveAPIView):
    queryset = News.objects.filter(active = True)
    serializer_class = NewsSerializer
    permission_classes = [AllowAny]
    lookup_field = "id"
    def get(self, request, api_token, *args, **kwargs):
        try:
            user = Profile.objects.get(api_token = api_token)
        except:
            return Response({
                "Error": "Sorry, an error occured"
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(self.get_object())

        return Response(serializer.data, status = status.HTTP_200_OK)

