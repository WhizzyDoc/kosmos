from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from rest_framework.decorators import APIView
from rest_framework.generics import GenericAPIView, RetrieveUpdateDestroyAPIView, ListCreateAPIView, CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import AllowAny, BasePermission
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.mixins import CreateModelMixin
from main.models import *
from django.contrib.auth.views import PasswordResetConfirmView
from admins.views import generate_token
from admins.models import *
from .serializers import *
import uuid
from main.utils import *

# Create your views here.

class LoginView(GenericAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        try:
            user_id = request.data["user_id"]
            try:
                username = Profile.objects.get(id_no=user_id).user.username
            except:
                return Response({
                    "error": "Invalid Details"
                }, status = status.HTTP_404_NOT_FOUND)
            user = get_object_or_404(User, username = username)

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
                log = Log.objects.create(
                    user = user,
                    action = "You logged in",
                    site = user_profile.site
                )
                log.save()
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
    serializer_class = ProfileSerializer

    def update(self, request, api_token, *args, **kwargs):
        try:
            user_profile = Profile.objects.get(api_token=api_token)
            user = user_profile.user
        except:
            return Response({
                "error": "an error occured"
            }, status = status.HTTP_400_BAD_REQUEST)

        # Update the user's password
        previous_password = request.data["prev_password"]
        new_password = request.data["new_password"]
        
        if user.check_password(previous_password):
            user.set_password(new_password)
            log = Log.objects.create(
                    user = user_profile,
                    action = "You updated your Password"
            )
            log.save()
            user.save()
        else:
            return Response({"error": "Invalid previous password"}, status=status.HTTP_400_BAD_REQUEST)

        # Serialize the updated user profile
        serializer = self.serializer_class(user_profile)
        
        return Response({
            "message": "Password Updated!",
            "user_profile": serializer.data
        }, status = status.HTTP_200_OK)

    def get(self, request, api_token, *args, **kwargs):
        try:
            user_profile = Profile.objects.get(api_token=api_token)
            user = user_profile.user
        except:
            return Response({
                "error": "an error occured"
            }, status = status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(user_profile)
        return Response(serializer.data, status = status.HTTP_200_OK)

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
            log = Log.objects.create(
            user = user,
            action = "You created your bank account"
            )
            log.save()
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

            log = Log.objects.create(
                    user = user,
                    action = "You updated your Bank Details"
            )
            log.save()
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



class CreateListEventView(ListAPIView):
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
        try:
            profile = Profile.objects.get(api_token = api_token)
            user_pk = profile.pk
        except: 
            return Response({
                "error": "Can't complete that action"
            })


        data = request.data.copy()
        
        data["employee"] = user_pk

        serializer = self.serializer_class(data = data)

        if serializer.is_valid():
            log = Log.objects.create(
                    user = profile,
                    action = "You lodged a complaint"
            )
            log.save()
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

        # Check if the user is the owner of the complaint or an admin
        if user_profile == complaint.employee:

            if 'title' in request.data or 'complaint' in request.data or 'proposed_solution' in request.data:
                data = request.data.copy()
                serializer = self.serializer_class(instance=complaint, data=data, partial=True)

                if serializer.is_valid():
                    log = Log.objects.create(
                            user = user_profile,
                            action = "You updated your complaint"
                    )
                    log.save()
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
            log = Log.objects.create(
                    user = user_profile,
                    action = "You deleted a complaint"
            )
            log.save()
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

class GroupChats(RetrieveAPIView):
    queryset = GroupChat.objects.all()
    serializer_class = GroupChatSerializer
    permission_classes = [AllowAny]

    def get(self, request, api_token, *args, **kwargs):
        try:
            user = Profile.objects.get(api_token = api_token)
            user_pk = user.pk
        except:
            return Response({
                "error": "An error occured!"
            }, status=status.HTTP_400_BAD_REQUEST)

        groups = user.department_group.all()

        serializer = self.serializer_class(groups, many = True)

        return Response(serializer.data, status = status.HTTP_200_OK)

class GroupChatDetailsView(RetrieveAPIView):
    queryset = GroupChat.objects.all()
    serializer_class = GroupChatSerializer
    permission_classes = [AllowAny]
    lookup_field = "id"

    def get(self, request, api_token,id, *args, **kwargs):
        try:
            user = Profile.objects.get(api_token = api_token)
        except:
            return Response({
                "Error": "Sorry, an error occured"
            }, status=status.HTTP_403_FORBIDDEN)
        if user.department_group.filter(id = id).exists():
            serializer = self.serializer_class(self.get_object())
        else:
            return Response({
                "Error": "Sorry, you are not in this group"
            }, status = status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.data, status = status.HTTP_200_OK)

class ChatMessageCreateView(ListCreateAPIView):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = [AllowAny]

    def get(self, request, api_token, pk, *args, **kwargs):
        id = pk
        try:
            user = Profile.objects.get(api_token = api_token)
            user_pk = user.pk
        except:
            return Response({
                "Error": "Sorry, an error occured"
            }, status=status.HTTP_403_FORBIDDEN)
        if user.department_group.filter(id = id).exists():
            serializer = ChatMessageSerializerGet(ChatMessage.objects.filter(group = id), many = True)
            return Response(serializer.data, status = status.HTTP_200_OK)
        else:
            return Response({
                "Error": "Sorry, you are not in this group"
            })


    def create(self, request, api_token, pk,  *args, **kwargs):
        id = pk
        try:
            user = Profile.objects.get(api_token = api_token)
            user_pk = user.pk
        except:
            return Response({
                "Error": "Sorry, an error occured"
            }, status=status.HTTP_403_FORBIDDEN)
        if user.department_group.filter(id = id).exists():
            # try:
            group = GroupChat.objects.get(id = id)

            data = request.data.copy()
            data["group"] = group.pk
            data["sender"] = user_pk
            
            serializer = self.serializer_class(data = data)
            if serializer.is_valid():
                serializer.save()
                
                return Response({
                    "message": serializer.data["message"],
                    "date": serializer.data["date"],
                    "group": group.title,
                    "sender": user.first_name + " " + user.last_name
                }, status = status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "Error": "Sorry, you are not in this group"
            }, status = status.HTTP_401_UNAUTHORIZED)

class QueryView(RetrieveAPIView):
    queryset = Query.objects.all()
    permission_classes = [AllowAny]
    serializer_class = QuerySerializer
    def get(self, request, api_token, format=None):
        
        try:
            user = Profile.objects.get(api_token = api_token)
            user_pk = user.pk
        except:
            return Response({
                "Error": "Sorry, an error occured"
                }, status=status.HTTP_403_FORBIDDEN)
        query_id = request.query_params.get("id")
        if query_id:
            try:
                query = Query.objects.get(id = query_id, addressed_to = user_pk)
                serializer = self.serializer_class(query)
                return Response(serializer.data, status = status.HTTP_200_OK)
            except:
                    return Response({
                        "details": "query not found"
                    }, status = status.HTTP_404_NOT_FOUND)
        query = Query.objects.filter(addressed_to = user_pk)
        serializer = self.serializer_class(query, many = True)
        return Response(serializer.data, status = status.HTTP_200_OK)
    
class LogView(RetrieveAPIView):
    queryset = Log.objects.all()
    permission_classes = [AllowAny]
    serializer_class = LogSerializer

    def get(self, request, api_token, *args, **kwargs):
        try:
            user = Profile.objects.get(api_token=api_token)
            user_pk = user.pk
        except Profile.DoesNotExist:
            return Response(
                {"Error": "Profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        logs = Log.objects.filter(user=user)

        serializer = self.serializer_class(logs, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

class NotificationsView(RetrieveAPIView):
    queryset = Notification.objects.all()
    permission_classes = [AllowAny]
    serializer_class = NotificationSerializer

    def get(self, request, api_token, *args, **kwargs):
        try:
            user = Profile.objects.get(api_token=api_token)
            user_pk = user.pk
        except Profile.DoesNotExist:
            return Response(
                {"Error": "Profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        notifications = Notification.objects.all()

        serializer = self.serializer_class(notifications, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

class ChangePassword(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):

        new_password = request.data["new_password"]
        old_password = request.data["old_password"]
        user_id = request.data["user_id"]
        print(user_id)
        print(new_password)
        print(old_password)

        try:
            # Check if details exist
            user_profile = Profile.objects.get(id_no = user_id)
            user = user_profile.user
            if user.check_password(old_password):
                user.set_password(new_password)
                user.save()

                return Response({
                    'message': 'Successfully changed password'
                }, status = status.HTTP_200_OK)
            else:
                return Response({
                    "error": "Your previous login details don't match!"
                }, status = status.HTTP_400_BAD_REQUEST)
        except:
            return Response({
                "details": "The data you entered don't match!"
            })

class ForgotPassword_GetNewPasswordView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        # Get user_id

        user_id = request.data["user_id"]
        try:
            user_profile = Profile.objects.get(id_no = user_id)
        except:
            return Response({
                "details": "not found"
            }, status = status.HTTP_404_NOT_FOUND)

        # Get user's email
        user_email = user_profile.email

        # Generate a new Password
        new_password = str(uuid.uuid4()).replace("-", "")[:9]

        # Save and Send user the new Password
        send_password_email(user_email, user_profile.first_name, new_password)
        #print(new_password)

        save_password = ForgottenPassword.objects.create(
            user = user_profile,
            temporary_password = new_password
        )
        save_password.save()
        return Response({
            "details": "Email Sent"
        }, status = status.HTTP_201_CREATED)


class ResetPassword(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):

        new_password = request.data["new_password"]
        user_id = request.data["user_id"]

        try:
            # Check if details exist
            user_profile = Profile.objects.get(id_no = user_id)
            
            forgot_id_details = ForgottenPassword.objects.get(user = user_profile.pk, temporary_password = new_password)
        except:
            return Response({
                "details": "The data you entered don't match!"
            })

        user_profile.user.password = forgot_id_details.temporary_password

        forgot_id_details.delete()

        return Response({
            "success": "You've successfully updated your password"
        }, status = status.HTTP_200_OK)


class TaskView(RetrieveAPIView):
    queryset = Task.objects.all()
    permission_classes = [AllowAny]
    serializer_class = TaskSerializer
    def get(self, request, api_token, format=None):
        
        try:
            user = Profile.objects.get(api_token = api_token)
            user_pk = user.pk
        except:
            return Response({
                "Error": "Sorry, an error occured"
                }, status=status.HTTP_403_FORBIDDEN)
        task_id = request.query_params.get("id")
        if task_id:
            try:
                task = Task.objects.get(id = task_id, assigned_to = user_pk)
                serializer = self.serializer_class(task)
                return Response(serializer.data, status = status.HTTP_200_OK)
            except:
                    return Response({
                        "details": "query not found"
                    }, status = status.HTTP_404_NOT_FOUND)
        task = Task.objects.filter(assigned_to = user_pk)
        serializer = self.serializer_class(task, many = True)
        return Response(serializer.data, status = status.HTTP_200_OK)
