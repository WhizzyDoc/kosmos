from rest_framework import generics, viewsets
from .models import *
from main.models import *
from employee.models import *
from .serializers import *
from .bank import bank_list
from .utils import create_action
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.contrib.auth.models import User, Group
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from rest_framework.decorators import action
from rest_framework import status
from django.contrib.auth import login, authenticate, logout
import secrets
import re
import json
from django.db.models import Q
from .encrypt_utils import encrypt, decrypt
from datetime import datetime, timedelta
from django.utils import timezone
from django.http import FileResponse
from django.utils.text import slugify
import random
import math
import string

employee_group, created = Group.objects.get_or_create(name="employee")
admin_group, created = Group.objects.get_or_create(name="admin")
staff_group, created = Group.objects.get_or_create(name="staff")

def slugify(s):
    s = s.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_-]+', '-', s)
    s = re.sub(r'^-+|-+$', '', s)
    return s
def join(s):
    s = s.strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_-]+', '', s)
    s = re.sub(r'^-+|-+$', '', s)
    return s

def generate_id(id):
    id = int(id)
    id_no = ""
    if id < 10:
        id_no = f'kos000{id}'
    elif id >= 10 and id < 100:
        id_no = f'kos00{id}'
    elif id >= 100 and id < 1000:
        id_no = f'kos0{id}'
    elif id >= 1000:
        id_no = f'kos{id}'
    return id_no
    

def generate_token():
    key = ''
    for i in range(60):
        rand_char = random.choice("abcdefghijklmnopqrstuvwxyz1234567890")
        key += rand_char
    return key

def sterilize(s):
    s = ''.join(letter for letter in s if letter.isalnum())
    return s

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if re.match(pattern, email):
        return True
    else:
        return False

def is_valid_password(password):
    if len(password) < 8:
        return False
    if not re.search(r'[a-zA-Z]', password) or not re.search(r'\d', password):
        return False
    return True

def is_valid_username(username):
    pattern = r'^[a-zA-Z0-9]+$'
    if re.match(pattern, username):
        return True
    else:
        return False

# create your views here

class SiteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer
    permission_classes = [AllowAny]
    @action(detail=False,
            methods=['get'])
    def get_site_info(self, request, *args, **kwargs):
        try:
            sites = Site.objects.all()
            if sites.exists():
                site = Site.objects.first()
                return Response({
                    'status': 'success',
                    'message': 'site info fetched successfully',
                    'data': SiteSerializer(site).data
                })
            else:
                return Response({
                    'status': 'success',
                    'message': 'Site info not found',
                })
        except:
            return Response({
                'status': 'error',
                'message': 'Error Occured'
            })
            
    @action(detail=False,
            methods=['post'])
    def create_site_info(self, request, *args, **kwargs):
        if request.method == 'POST':
            api_token = request.POST.get('api_token')
            title = request.POST.get('title')
            tagline = request.POST.get('tagline')
            about = request.POST.get('about')
            email = request.POST.get("email")
            objectives = request.POST.get('objectives')
            mission = request.POST.get('mission')
            logo = None
            if request.FILES:
                logo = request.FILES.get('logo')
            try:
                profile = Profile.objects.get(api_token=api_token)
                user = profile.user
                if admin_group in user.groups.all():
                    try:
                        site = Site.objects.first()
                        if site is not None:
                            return Response({
                                'status': 'error',
                                'message': 'site already exists, edit site info instead'
                            })
                        new_site = Site(title=title, tagline=tagline, logo=logo, about=about, objectives=objectives,
                                        mission=mission, company_email=email)
                        new_site.save()
                        return Response({
                            'status': 'success',
                            'message': 'site created sucessfully',
                            'data': SiteSerializer(new_site).data
                        })
                    except:
                        return Response({
                            'status': 'error',
                            'message': 'error while creating site info'
                        })
                else:
                    return Response({
                        'status': 'error',
                        'message': 'user not authorized'
                    })
            except:
                return Response({
                    'status': 'error',
                    'message': 'user not found'
                })  
        else:
            return Response({
                'status': 'error',
                'message': 'GET method not allowed'
            })
    @action(detail=False,
            methods=['post'])
    def edit_site_info(self, request, *args, **kwargs):
        if request.method == 'POST':
            api_token = request.POST.get('api_token')
            title = request.POST.get('title')
            tagline = request.POST.get('tagline')
            about = request.POST.get('about')
            email = request.POST.get("email")
            objectives = request.POST.get('objectives')
            mission = request.POST.get('mission')
            logo = request.FILES.get('logo')
            try:
                profile = Profile.objects.get(api_token=api_token)
                user = profile.user
                if admin_group in user.groups.all():
                    try:
                        sites = Site.objects.all()
                        if sites.exists():
                            site = Site.objects.first()
                            if title:
                                site.title = title
                                site.save()
                            if email:
                                site.company_email = email
                                site.save()
                            if tagline:
                                site.tagline = tagline
                                site.save()
                            if about:
                                site.about = about
                                site.save()
                            if objectives:
                                site.objectives = objectives
                                site.save()
                            if mission:
                                site.mission = mission
                                site.save()
                            if logo:
                                site.logo = logo
                                site.save()
                            return Response({
                                'status': 'success',
                                'message': 'site info edited successfully',
                                'data': SiteSerializer(site).data
                            })
                        else:
                            return Response({
                                'status': 'error',
                                'message': 'site info not found'
                            })
                    except:
                        return Response({
                            'status': 'error',
                            'message': 'error occured'
                        })
                else:
                    return Response({
                        'status': 'error',
                        'message': 'user not authorized'
                    })
            except:
                return Response({
                    'status': 'error',
                    'message': 'user not found'
                })
        else:
            return Response({
                'status': 'error',
                'message': 'GET method not allowed'
            })
            
class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]
    @action(detail=False,
            methods=['post'])
    def create_admin_account(self, request, *args, **kwargs):
        email = request.POST.get('email')
        f_name = request.POST.get('first_name')
        l_name = request.POST.get('last_name')
        m_name = request.POST.get('middle_name')
        nationality = request.POST.get('nationality')
        phone_number = request.POST.get('phone_number')
        image = request.FILES.get('image')
        username = request.POST.get('username')
        password = request.POST.get('password')
        #check if email is valid
        if not is_valid_email(email):
            return Response({
                'status': 'error',
                'message': f"Invalid email",
            })
        if not is_valid_username(username):
            return Response({
                'status': 'error',
                'message': f"Invalid username",
            })
        if not is_valid_password(password):
            return Response({
                'status': 'error',
                'message': f"Invalid password",
            })
        try:
            admin = User.objects.get(groups=admin_group)
            if admin is not None:
                return Response({
                    'status': 'error',
                    'message': f'An admin account already exists.',
                })
            new_user = User.objects.create(email=email, first_name=f_name, last_name=l_name, username=username, is_superuser=True, is_staff=True)
            new_user.set_password(password)
            new_user.save()
            new_user.groups.add(admin_group)
            new_user.save()
            try:
                api_key = generate_token()
                # create a new profile
                new_profile = Profile(user=new_user, email=email, first_name=f_name, last_name=l_name, api_token=api_key,
                                      middle_name=m_name, nationality=nationality, phone_number=phone_number, image=image)
                new_profile.save()
                return Response({
                        'status': 'success',
                        'message': f'Admin account created successfully',
                        'data': ProfileSerializer(new_profile).data
                    })
            except:
                return Response({
                    'status': 'error',
                    'message': f'Admin account created, Error generating profile',
                })
        except:
            return Response({
                'status': 'error',
                'message': f'Error occured while creating account',
            })
    
    @action(detail=False,
            methods=['post'])
    def forgot_password(self, request, *args, **kwargs):
        email = request.POST.get('email')
        if not is_valid_email(email):
            return Response({
                'status': 'error',
                'message': f"Invalid email",
            }) 
        try: 
            user = User.objects.get(email=email)
            if admin_group in user.groups.all():
                token = get_random_string(length=32)
                user.set_password(token)
                user.save()
                # send email
                subject = 'Password Reset Request'
                message = f'Your new temporary password is: {token}'
                from_email = 'your_email@example.com'
                recipient_list = [email]
                send_mail(subject, message, from_email, recipient_list, fail_silently=False)
                return Response({
                    'status': 'success',
                    'message': f'Password reset instructions has been sent to {email}'
                })
            else:
                return Response({
                'status': 'error',
                'message': f"Unauthorized email",
            }) 
        except User.DoesNotExist: 
            return Response({
                'status': 'error',
                'message': f"Unregistered email",
            }) 
    @action(detail=False,
            methods=['post'])
    def change_password(self, request, *args, **kwargs):
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        key = request.POST.get('api_token')
        if not is_valid_password(new_password):
            return Response({
                'status': 'error',
                'message': f"Invalid new password combination",
            }) 
        try:
            profile = Profile.objects.get(api_token=key)
            admin = profile.user
            if admin_group in admin.groups.all():
                try:
                    user = authenticate(request, username=admin.username, password=old_password)
                    if user is not None:
                        user.set_password(new_password)
                        user.save()
                        return Response({
                            'status': "success",
                            "message": "password changed successfully",
                        })
                    else:
                        return Response({
                            'status': "error",
                            "message": "Incorrect password",
                        }) 
                except: 
                    return Response({
                        'status': "error",
                        "message": "error while changing password",
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })
        
    @action(detail=False,
            methods=['post'])
    def create_employee_account(self, request, *args, **kwargs):
        email = request.POST.get('email')
        title = request.POST.get('title')
        f_name = request.POST.get('first_name')
        l_name = request.POST.get('last_name')
        m_name = request.POST.get('middle_name')
        city = request.POST.get('city')
        state = request.POST.get('state')
        nationality = request.POST.get('nationality')
        phone_number = request.POST.get('phone_number')
        a_type = request.POST.get('account_type')
        salary = request.POST.get('salary')
        position = request.POST.get('position')
        department = request.POST.get('department')
        key = request.POST.get('api_token')
        try:
            profile = Profile.objects.get(api_token=key)
            user_p = profile.user
            if admin_group in user_p.groups.all():
                try:
                    # check if email is valid (view.py line 49)
                    if is_valid_email(email):
                        emails = []
                        users = User.objects.all()
                        # get a list of all registered emails
                        for user in users:
                            emails.append(user.email)
                        # check if email is not in existence
                        if email not in emails:
                            # check account type and retrieve appropriate group
                            try:
                                new_user = User.objects.create(email=email, first_name=f_name, last_name=l_name)
                                new_user.set_password(f_name)
                                new_user.save()
                                id_no = generate_id(new_user.id)
                                new_user.username = id_no
                                new_user.save()
                                if a_type == 'staff':
                                    new_user.groups.add(staff_group)
                                    new_user.save()
                                elif a_type == 'employee':
                                    new_user.groups.add(employee_group)
                                    new_user.save()
                                # creates a new API key for user instance
                                api_key = generate_token()
                                # create a new profile
                                new_profile = Profile(user=new_user, email=email, id_no=id_no, first_name=f_name, last_name=l_name,
                                                    api_token=api_key, middle_name=m_name, nationality=nationality, phone_number=phone_number,
                                                    salary=salary, title=title, city=city, state=state)
                                new_profile.save()
                                Log.objects.create(user=profile, action=f"created a new employee ID number {id_no}")
                                if position is not None and str(position) != '':
                                    try:
                                        p = Position.objects.get(id=int(position))
                                        new_profile.position = p
                                        new_profile.save()
                                    except:
                                        return Response({
                                            'status': 'error',
                                            'message': 'Invalid id for position'
                                        })
                                if department is not None and str(department) != '':
                                    try:
                                        d = Department.objects.get(id=int(department))
                                        new_profile.department = d
                                        new_profile.save()
                                        g = GroupChat.objects.get(department=d)
                                        g.members.add(new_profile)
                                        g.save()
                                    except:
                                        return Response({
                                            'status': 'error',
                                            'message': 'Invalid id for department'
                                        })
                                return Response({
                                    'status': 'success',
                                    'message': f'Account created successfully. username is {id_no} and password is {f_name}',
                                    'data': ProfileSerializer(new_profile).data
                                })
                            except:
                                return Response({
                                    'status': 'error',
                                    'message': f'Error occured while creating account',
                                })
                        else:
                            return Response({
                                'status': 'error',
                                'message': f'Email \'{email}\' has already been used, kindly use another email',
                            })
                    else:
                        return Response({
                            'status': 'error',
                            'message': f"Invalid email",
                        })
                except:
                    return Response({
                        'status': 'error',
                        'message': f"Error while creating a new employee",
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })

    # to register the created account by filling profile details
    @action(detail=False,
            methods=['post'])
    def register(self, request, *args, **kwargs):
        email = request.POST.get('email')
        dob = request.POST.get('date_of_birth')
        a_date = request.POST.get('appointment_date')
        address = request.POST.get('address')
        image = request.FILES.get('image')
        #id_no = ''
        # check if post email data is valid
        try:
            if is_valid_email(email):
                profile = Profile.objects.get(email=email)
                if profile is not None:
                    profile.date_of_birth = dob
                    profile.appointment_date = a_date
                    profile.address = address
                    profile.image = image
                    profile.save()
                    return Response({
                        'status': 'success',
                        'data': ProfileSerializer(profile).data,
                        'message': 'User registration succesful!'
                    })
                else:
                    return Response({
                        'status': 'error',
                        'message': f'user not found for email {email}'
                    })
            else:
                return Response({
                    'status': 'error',
                    'message': f'Invalid email'
                })
        except:
            return Response({
                'status': 'error',
                'message': f'Error while registering account'
            })
                
                
    @action(detail=False,
            methods=['post'])
    def authentication(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                if admin_group in user.groups.all():
                    login(request, user)
                    profile = get_object_or_404(Profile, user=user)
                    return Response({
                        'status': "success",
                        "message": "login successful",
                        "data": ProfileSerializer(profile).data,
                    })
                else:
                    return Response({
                        'status': 'error',
                        'message': "User is not authorized",
                    })
            else:
                return Response({
                    'status': 'error',
                    'message': "Your account has been disabled",
                })
        else:
            return Response({
                'status': 'error',
                'message': "Invalid login credentials",
            })
    @action(detail=False,
            methods=['post'])
    def admin_logout(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                user.is_authenticated = False
                user.save()
                return Response({
                    'status': "success",
                    "message": "logout successful"
                })
            else:
                return Response({
                    'status': 'error',
                    'message': "User is not authorized",
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })
    @action(detail=False,
            methods=['post'])
    def get_admin_profile(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                return Response({
                    'status': "success",
                    "message": "data fetched successfully",
                    "data": ProfileSerializer(profile).data,
                })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })
    @action(detail=False,
            methods=['post'])
    def edit_admin_profile(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                # edited attributes
                Log.objects.create(user=profile, action=f"edited admin profile")
                return Response({
                    'status': "success",
                    "message": "profile edited successfully",
                    "data": ProfileSerializer(profile).data,
                })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })
        

class PositionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = [AllowAny]
    # to get all positions to includ in registration form data
    @action(detail=False,
            methods=['get'])
    def get_positions(self, request, *args, **kwargs):
        page = self.request.query_params.get('page')
        per_page = self.request.query_params.get('per_page')
        query = self.request.query_params.get('search')
        try:
            if page is None:
                page = 1
            else:
                page = int(page)
            if per_page is None:
                per_page = 20
            else:
                per_page = int(per_page)
            if query is None:
                query = ""
            start = (page - 1) * per_page
            stop = page * per_page
            total_items = Position.objects.filter(title__icontains=query).count()
            total_pages = math.ceil(total_items/per_page)
            positions = Position.objects.filter(title__icontains=query)[start:stop]
            if positions.exists():
                return Response({
                    'status': 'success',
                    'data': [PositionSerializer(pos).data for pos in positions],
                    'message': 'position list retrieved',
                    'page_number': page,
                    "list_per_page": per_page,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "search_query": query
                })
            else:
                return Response({
                    'status': 'success',
                    'message': 'No position found',
                    'page_number': page,
                    "list_per_page": per_page,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "search_query": query
                })
        except:
            return Response({
                'status': 'error',
                'message': 'Error getting position list'
            })
    @action(detail=False,
            methods=['get'])
    def get_position(self, request, *args, **kwargs):
        id = self.request.query_params.get('position_id')
        if id:
            try:
                position = Position.objects.get(id=int(id))
                if position is not None:
                    return Response({
                        'status': 'success',
                        'data': PositionSerializer(position).data,
                        'message': 'position details retrieved'
                    })
                else:
                    return Response({
                        'status': 'success',
                        'message': 'Invalid position ID'
                    })
            except:
                return Response({
                    'status': 'error',
                    'message': 'Invalid position ID'
                })
        else:
            return Response({
                'status': 'success',
                'message': 'Invalid position ID'
            })
    @action(detail=False,
            methods=['post'])
    def create_position(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        title = request.POST.get('title')
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                # check if position does not exist
                position = Position.objects.get(title=title)
                if position is not None:
                    return Response({
                        'status': "error",
                        "message": "position already exists!"
                    })
                else:
                    new_pos = Position(title=title)
                    new_pos.save()
                    Log.objects.create(user=profile, action=f"created a new position {title}")
                    return Response({
                        'status': "success",
                        "message": "position created sucessfully",
                        "data": PositionSerializer(new_pos).data,
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })
    @action(detail=False,
            methods=['post'])
    def edit_position(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        title = request.POST.get('title')
        id = int(request.POST.get('id'))
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                try:
                    position = Position.objects.get(id=id)
                    position.title = title
                    position.save()
                    Log.objects.create(user=profile, action=f"edited position {position.title}")
                    return Response({
                        'status': "success",
                        "message": "position edited sucessfully",
                        "data": PositionSerializer(position).data,
                    })
                except:
                    return Response({
                        "status": "error",
                        "message": f"position  with id \'{id}\' does not exist"
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })
    @action(detail=False,
            methods=['post'])
    def delete_position(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        id = int(request.POST.get('id'))
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                try:
                    position = Position.objects.get(id=id)
                    position.delete()
                    Log.objects.create(user=profile, action=f"deleted position {position.title}")
                    return Response({
                        'status': "success",
                        "message": f"position \'{position.title}\' deleted sucessfully",
                    })
                except:
                    return Response({
                        "status": "error",
                        "message": f"position  with id \'{id}\' does not exist"
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })

class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [AllowAny]
    # to get all departments to include in registration form data
    @action(detail=False,
            methods=['get'])
    def get_departments(self, request, *args, **kwargs):
        page = self.request.query_params.get('page')
        per_page = self.request.query_params.get('per_page')
        query = self.request.query_params.get('search')
        try:
            if page is None:
                page = 1
            else:
                page = int(page)
            if per_page is None:
                per_page = 20
            else:
                per_page = int(per_page)
            if query is None:
                query = ""
            start = (page - 1) * per_page
            stop = page * per_page
            total_items = Department.objects.filter(title__icontains=query).count()
            total_pages = math.ceil(total_items/per_page)
            departments = Department.objects.filter(title__icontains=query)[start:stop]
            if departments.exists():
                return Response({
                    'status': 'success',
                    'data': [DepartmentSerializer(dept).data for dept in departments],
                    'message': 'department list retrieved',
                    'page_number': page,
                    "list_per_page": per_page,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "search_query": query
                })
            else:
                return Response({
                    'status': 'success',
                    'message': 'No department found',
                    'page_number': page,
                    "list_per_page": per_page,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "search_query": query
                })
        except:
            return Response({
                'status': 'error',
                'message': 'Error getting department list'
            })
    @action(detail=False,
            methods=['get'])
    def get_department(self, request, *args, **kwargs):
        id = self.request.query_params.get('department_id')
        if id:
            try:
                department = Department.objects.get(id=int(id))
                if department is not None:
                    return Response({
                        'status': 'success',
                        'data': DepartmentSerializer(department).data,
                        'message': 'department details retrieved'
                    })
                else:
                    return Response({
                        'status': 'success',
                        'message': 'Invalid department ID'
                    })
            except:
                return Response({
                    'status': 'error',
                    'message': 'Invalid department ID'
                })
        else:
            return Response({
                'status': 'success',
                'message': 'Invalid department ID'
            })
    @action(detail=False,
            methods=['post'])
    def create_department(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        title = request.POST.get('title')
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                # check if position does not exist
                department = Department.objects.get(title=title)
                if department is not None:
                    return Response({
                        'status': "error",
                        "message": "department already exists!"
                    })
                else:
                    new_dep = Department(title=title)
                    new_dep.save()
                    new_group_chat = GroupChat(title=f"Group Chat for {new_dep.title}",
                                               department=new_dep)
                    new_group_chat.save()
                    Log.objects.create(user=profile, action=f"created a new department {new_dep.title}")
                    return Response({
                        'status': "success",
                        "message": "department created sucessfully",
                        "data": DepartmentSerializer(new_dep).data,
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })
    @action(detail=False,
            methods=['post'])
    def edit_department(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        title = request.POST.get('title')
        id = int(request.POST.get('id'))
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                try:
                    department = Department.objects.get(id=id)
                    department.title = title
                    department.save()
                    group_chat = GroupChat.objects.get(department=department)
                    group_chat.title = f'Group chat for {title}'
                    group_chat.save()
                    Log.objects.create(user=profile, action=f"edited department {department.title}")
                    return Response({
                        'status': "success",
                        "message": "department edited sucessfully",
                        "data": DepartmentSerializer(department).data,
                    })
                except:
                    return Response({
                        "status": "error",
                        "message": f"department  with id \'{id}\' does not exist"
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })
    @action(detail=False,
            methods=['post'])
    def delete_department(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        id = int(request.POST.get('id'))
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                try:
                    department = Department.objects.get(id=id)
                    group_chat = GroupChat.objects.get(department=department)
                    group_chat.delete()
                    department.delete()
                    Log.objects.create(user=profile, action=f"deleted department {department.title} and its group chat")
                    return Response({
                        'status': "success",
                        "message": f"department \'{department.title}\' deleted sucessfully",
                    })
                except:
                    return Response({
                        "status": "error",
                        "message": f"department  with id \'{id}\' does not exist"
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })

class BankViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Bank.objects.all()
    serializer_class = BankSerializer
    permission_classes = [AllowAny]
    # to get all banks to includ in registration form data
    @action(detail=False,
            methods=['get'])
    def get_banks(self, request, *args, **kwargs):
        page = self.request.query_params.get('page')
        per_page = self.request.query_params.get('per_page')
        query = self.request.query_params.get('search')
        try:
            if page is None:
                page = 1
            else:
                page = int(page)
            if per_page is None:
                per_page = 20
            else:
                per_page = int(per_page)
            if query is None:
                query = ""
            start = (page - 1) * per_page
            stop = page * per_page
            total_items = Bank.objects.filter(Q(bank_name__icontains=query) | Q(bank_code__icontains=query)).count()
            total_pages = math.ceil(total_items/per_page)
            banks = Bank.objects.filter(Q(bank_name__icontains=query) | Q(bank_code__icontains=query))
            if banks.exists():
                return Response({
                    'status': 'success',
                    'data': [BankSerializer(bank).data for bank in banks],
                    'message': 'bank list retrieved',
                    'page_number': page,
                    "list_per_page": per_page,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "search_query": query
                })
            else:
                return Response({
                    'status': 'success',
                    'message': 'No bank found',
                    'page_number': page,
                    "list_per_page": per_page,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "search_query": query
                })
        except:
            return Response({
                'status': 'error',
                'message': 'Error getting bank list'
            })
    """
    @action(detail=False,
            methods=['get'])
    def build_bank(self, request, *args, **kwargs):
        try:
            for b in bank_list:
                bank = Bank(bank_name=b['name'], bank_code=b['code'])
                bank.save()
            return Response({
                'status': 'success'
            })
        except:
            return Response({
                'status': 'error'
            })
    """
    @action(detail=False,
            methods=['post'])
    def create_bank(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        name = request.POST.get('bank_name')
        code = request.POST.get('bank_code')
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                # check if position does not exist
                bank = Bank.objects.get(bank_name=name, bank_code=code)
                if bank is not None:
                    return Response({
                        'status': "error",
                        "message": "bank already exists!"
                    })
                else:
                    new_bank = Bank(bank_name=name, bank_code=code)
                    new_bank.save()
                    Log.objects.create(user=profile, action=f"created a new bank {name}")
                    return Response({
                        'status': "success",
                        "message": "bank created sucessfully",
                        "data": BankSerializer(new_bank).data,
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "profile not found"
            })
    @action(detail=False,
            methods=['post'])
    def edit_bank(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        name = request.POST.get('bank_name')
        code = request.POST.get('bank_code')
        id = int(request.POST.get('id'))
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                try:
                    bank = Bank.objects.get(id=id)
                    if name is not None:
                        bank.bank_name = name
                        bank.save()
                    if code is not None:
                        bank.bank_code = code
                        bank.save()
                        Log.objects.create(user=profile, action=f"edited bank {name}")
                    return Response({
                        'status': "success",
                        "message": "bank edited sucessfully",
                        "data": BankSerializer(bank).data,
                    })
                except:
                    return Response({
                        "status": "error",
                        "message": f"bank with id \'{id}\' does not exist"
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "profile not found"
            })
    @action(detail=False,
            methods=['post'])
    def delete_bank(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        id = int(request.POST.get('id'))
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                try:
                    bank = Bank.objects.get(id=id)
                    bank.delete()
                    Log.objects.create(user=profile, action=f"deleted bank {bank.bank_name}")
                    return Response({
                        'status': "success",
                        "message": f"bank \'{bank.bank_name}\' deleted sucessfully",
                    })
                except:
                    return Response({
                        "status": "error",
                        "message": f"bank  with id \'{id}\' does not exist"
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "profile not found"
            })

class NewsCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NewsCategory.objects.all()
    serializer_class = NewsCategorySerializer
    permission_classes = [AllowAny]
    @action(detail=False,
            methods=['get'])
    def get_categories(self, request, *args, **kwargs):
        page = self.request.query_params.get('page')
        per_page = self.request.query_params.get('per_page')
        query = self.request.query_params.get('search')
        try:
            if page is None:
                page = 1
            else:
                page = int(page)
            if per_page is None:
                per_page = 20
            else:
                per_page = int(per_page)
            if query is None:
                query = ""
            start = (page - 1) * per_page
            stop = page * per_page
            total_items = NewsCategory.objects.filter(title__icontains=query).count()
            total_pages = math.ceil(total_items/per_page)
            categories = NewsCategory.objects.filter(title__icontains=query)
            if categories.exists():
                return Response({
                    'status': 'success',
                    'data': [NewsCategorySerializer(cat).data for cat in categories],
                    'message': 'category list retrieved',
                    'page_number': page,
                    "list_per_page": per_page,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "search_query": query
                })
            else:
                return Response({
                    'status': 'success',
                    'message': 'No categories found',
                    'page_number': page,
                    "list_per_page": per_page,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "search_query": query
                })
        except:
            return Response({
                'status': 'error',
                'message': 'Error getting categories list'
            })
    @action(detail=False,
            methods=['post'])
    def create_category(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        title = request.POST.get('title')
        slug = slugify(title)
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                # check if category does not exist
                category = NewsCategory.objects.get(slug=slug)
                if category is not None:
                    return Response({
                        'status': "error",
                        "message": "category already exists!"
                    })
                else:
                    new_cat = NewsCategory(title=title, slug=slug)
                    new_cat.save()
                    Log.objects.create(user=profile, action=f"created a news category {title}")
                    return Response({
                        'status': "success",
                        "message": "category created sucessfully",
                        "data": NewsCategorySerializer(new_cat).data,
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })
    @action(detail=False,
            methods=['post'])
    def edit_category(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        title = request.POST.get('title')
        slug = slugify(title)
        id = int(request.POST.get('id'))
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                try:
                    category = NewsCategory.objects.get(id=id)
                    category.title = title
                    category.slug = slug
                    category.save()
                    Log.objects.create(user=profile, action=f"edited news category {category.title}")
                    return Response({
                        'status': "success",
                        "message": "category edited sucessfully",
                        "data": NewsCategorySerializer(category).data,
                    })
                except:
                    return Response({
                        "status": "error",
                        "message": f"category  with id \'{id}\' does not exist"
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "invalid API token"
            })
    @action(detail=False,
            methods=['post'])
    def delete_category(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        id = int(request.POST.get('id'))
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                try:
                    category = NewsCategory.objects.get(id=id)
                    category.delete()
                    Log.objects.create(user=profile, action=f"deleted category {category.title}")
                    return Response({
                        'status': "success",
                        "message": f"category \'{category.title}\' deleted sucessfully",
                    })
                except:
                    return Response({
                        "status": "error",
                        "message": f"category  with id \'{id}\' does not exist"
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })

class EmployeeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]
    @action(detail=False,
            methods=['get'])
    def get_employees(self, request, *args, **kwargs):
        page = self.request.query_params.get('page')
        per_page = self.request.query_params.get('per_page')
        query = self.request.query_params.get('search')
        try:
            if page is None:
                page = 1
            else:
                page = int(page)
            if per_page is None:
                per_page = 20
            else:
                per_page = int(per_page)
            if query is None:
                query = ""
            start = (page - 1) * per_page
            stop = page * per_page
            total_items = Profile.objects.exclude(user__groups=admin_group).filter(
                Q(first_name__icontains=query) | Q(middle_name__icontains=query) |
                Q(last_name__icontains=query) | Q(email__icontains=query) |
                Q(phone_number__icontains=query)).count()
            total_pages = math.ceil(total_items/per_page)
            employees = Profile.objects.exclude(user__groups=admin_group).filter(
                Q(first_name__icontains=query) | Q(middle_name__icontains=query) |
                Q(last_name__icontains=query) | Q(email__icontains=query) |
                Q(phone_number__icontains=query))[start:stop]
            if employees.exists():
                return Response({
                    'status': 'success',
                    'data': [ProfileSerializer(pos).data for pos in employees],
                    'message': 'employee list retrieved',
                    'page_number': page,
                    "list_per_page": per_page,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "search_query": query
                })
            else:
                return Response({
                    'status': 'success',
                    'message': 'No employee found',
                    'page_number': page,
                    "list_per_page": per_page,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "search_query": query
                })
        except:
            return Response({
                'status': 'error',
                'message': 'Error getting employee list'
            })
        
    @action(detail=False,
            methods=['get'])
    def filter_employee(self, request, *args, **kwargs):
        page = self.request.query_params.get('page')
        per_page = self.request.query_params.get('per_page')
        dept_filter = self.request.query_params.get('department_id')
        state_filter = self.request.query_params.get('state')
        try:
            if dept_filter:
                try:
                    dept = Department.objects.get(id=int(dept_filter))
                    if page is None:
                        page = 1
                    else:
                        page = int(page)
                    if per_page is None:
                        per_page = 20
                    else:
                        per_page = int(per_page)
                    start = (page - 1) * per_page
                    stop = page * per_page
                    total_items = Profile.objects.exclude(user__groups=admin_group).filter(department=dept).count()
                    total_pages = math.ceil(total_items/per_page)
                    employees = Profile.objects.exclude(user__groups=admin_group).filter(department=dept)[start:stop]
                    if employees.exists():
                        return Response({
                            'status': 'success',
                            'data': [ProfileSerializer(pos).data for pos in employees],
                            'message': 'employee list retrieved',
                            'page_number': page,
                            "list_per_page": per_page,
                            "total_pages": total_pages,
                            "total_items": total_items,
                            "department": str(dept.title)
                        })
                    else:
                        return Response({
                            'status': 'success',
                            'message': 'No employees found',
                            'page_number': page,
                            "list_per_page": per_page,
                            "total_pages": total_pages,
                            "total_items": total_items,
                            "department": str(dept.title)
                        })
                except:
                    return Response({
                        "status": "error",
                        "message": "Invalid id for department"
                    })
            else:
                return Response({
                    "status": "error",
                    "message": "Invalid id for department"
                })
        except:
            return Response({
                "status": "error",
                "message": "error while getting employee list"
            })
    @action(detail=False,
            methods=['get'])
    def get_employee(self, request, *args, **kwargs):
        query = self.request.query_params.get('employee_id')
        if query and query != "":
            try:
                employee = Profile.objects.get(id_no=query)
                if employee is not None:
                    return Response({
                        'status': 'success',
                        'message': 'employee details retrieved',
                        'data': ProfileSerializer(employee).data
                    })
                else:
                    return Response({
                        'status': 'error',
                        'message': 'invalid ID number'
                    })
            except:
                return Response({
                    'status': 'error',
                    'message': 'invalid ID number'
                })
        else:
            return Response({
                'status': 'error',
                'message': 'invalid ID number'
            })
    @action(detail=False,
            methods=['get'])
    def get_employee_report(self, request, *args, **kwargs):
        query = self.request.query_params.get('employee_id')
        if query and query != "":
            try:
                employee = Profile.objects.get(id_no=query)
                if employee is not None:
                    tasks = Task.objects.filter(assigned_to=employee)
                    tasks_count = tasks.count()
                    completed_tasks = Task.objects.filter(assigned_to=employee, completed=True)
                    incomplete_tasks = Task.objects.filter(assigned_to=employee, completed=False)
                    return Response({
                        'status': 'success',
                        'message': 'employee tasks report retrieved',
                        'data': [TaskSerializer(task).data for task in tasks],
                        'total_tasks': tasks_count,
                        'completed_tasks': completed_tasks,
                        'incomplete_tasks': incomplete_tasks
                    })
                else:
                    return Response({
                        'status': 'error',
                        'message': 'invalid ID number'
                    })
            except:
                return Response({
                    'status': 'error',
                    'message': 'invalid ID number'
                })
        else:
            return Response({
                'status': 'error',
                'message': 'invalid ID number'
            })
    @action(detail=False,
            methods=['post'])
    def deactivate_employee(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        id = request.POST.get('id_number')
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                try:
                    employee = Profile.objects.get(id_no=id)
                    employee.user.is_active = False
                    employee.user.save()
                    Log.objects.create(user=profile, action=f"deactivated employee account ID {employee.id_no}")
                    return Response({
                        'status': "success",
                        "message": f"Employee \'{employee.first_name} {employee.last_name}\' account deactivated sucessfully",
                    })
                except:
                    return Response({
                        "status": "error",
                        "message": f"employee  with id \'{id}\' does not exist"
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })
    @action(detail=False,
            methods=['post'])
    def delete_employee(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        id = request.POST.get('id_number')
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                try:
                    employee = Profile.objects.get(id_no=id)
                    employee.user.delete()
                    employee.delete()
                    Log.objects.create(user=profile, action=f"deleted employee account ID {employee.id_no}")
                    return Response({
                        'status': "success",
                        "message": f"Employee \'{employee.first_name} {employee.last_name}\' deleted sucessfully",
                    })
                except:
                    return Response({
                        "status": "error",
                        "message": f"employee  with id \'{id}\' does not exist"
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })
     
class NewsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    permission_classes = [AllowAny]
    @action(detail=False,
            methods=['get'])
    def news_list(self, request, *args, **kwargs):
        page = self.request.query_params.get('page')
        per_page = self.request.query_params.get('per_page')
        query = self.request.query_params.get('search')
        try:
            if page is None:
                page = 1
            else:
                page = int(page)
            if per_page is None:
                per_page = 20
            else:
                per_page = int(per_page)
            if query is None:
                query = ""
            start = (page - 1) * per_page
            stop = page * per_page
            total_items = News.objects.filter(Q(title__icontains=query) |
                                              Q(post__icontains=query)).count()
            total_pages = math.ceil(total_items/per_page)
            news = News.objects.filter(Q(title__icontains=query) |
                                        Q(post__icontains=query))[start:stop]
            if news.exists():
                return Response({
                    'status': 'success',
                    'data': [NewsSerializer(ne).data for ne in news],
                    'message': 'news list retrieved',
                    'page_number': page,
                    "list_per_page": per_page,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "search_query": query
                })
            else:
                return Response({
                    'status': 'success',
                    'message': 'No news found',
                    'page_number': page,
                    "list_per_page": per_page,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "search_query": query
                })
        except:
            return Response({
                'status': 'error',
                'message': 'Error getting news list'
            })
    @action(detail=False,
            methods=['get'])
    def filter_news(self, request, *args, **kwargs):
        page = self.request.query_params.get('page')
        per_page = self.request.query_params.get('per_page')
        active_filter = self.request.query_params.get('active')
        verify_filter = self.request.query_params.get('verified')
        #cat_filter = self.request.query_params.get('category_id')
        try:
            if page is None:
                page = 1
            else:
                page = int(page)
            if per_page is None:
                per_page = 20
            else:
                per_page = int(per_page)
            if active_filter is None:
                active_filter = True
            elif active_filter.lower() == 'true':
                active_filter = True
            elif active_filter.lower() == 'false':
                active_filter = False
            else:
                active_filter = True
            if verify_filter is None:
                verify_filter = True
            elif verify_filter.lower() == 'true':
                verify_filter = True
            elif verify_filter.lower() == 'false':
                verify_filter = False
            else:
                verify_filter = True
            start = (page - 1) * per_page
            stop = page * per_page
            total_items = News.objects.filter(active=active_filter, verified=verify_filter).count()
            total_pages = math.ceil(total_items/per_page)
            news = News.objects.filter(active=active_filter, verified=verify_filter)[start:stop]
            if news.exists():
                return Response({
                    'status': 'success',
                    'data': [NewsSerializer(ne).data for ne in news],
                    'message': 'news list retrieved',
                    'page_number': page,
                    "list_per_page": per_page,
                    "total_pages": total_pages,
                    "total_items": total_items
                })
            else:
                return Response({
                    'status': 'success',
                    'message': 'No news found',
                    'page_number': page,
                    "list_per_page": per_page,
                    "total_pages": total_pages,
                    "total_items": total_items
                })
        except:
            return Response({
                'status': 'error',
                'message': 'Error getting news list'
            })
    @action(detail=False,
        methods=['get'])
    def get_news(self, request, *args, **kwargs):
        id = self.request.query_params.get('news_id')
        if id:
            try:
                news = News.objects.get(id=int(id))
                if news is not None:
                    return Response({
                        'status': 'success',
                        'data': NewsSerializer(news).data,
                        'message': 'news details retrieved'
                    })
                else:
                    return Response({
                        'status': 'success',
                        'message': 'Invalid news ID'
                    })
            except:
                return Response({
                    'status': 'error',
                    'message': 'Invalid news ID'
                })
        else:
            return Response({
                'status': 'error',
                'message': 'Invalid news ID'
            })
    @action(detail=False,
            methods=['post'])
    def create_news(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        title = request.POST.get('title')
        slug = slugify(title)
        post = request.POST.get('post')
        active = request.POST.get('active')
        verified = request.POST.get('verified')
        cat_id = int(request.POST.get('category_id'))
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                try:
                    category = NewsCategory.objects.get(id=cat_id)
                    try:
                        news = News(author=profile, title=title, slug=slug, post=post,
                                        category=category, active=active, verified=verified)
                        news.save()
                        Log.objects.create(user=profile, action=f"created a new post {title}")
                        create_action(profile, "added a news post", news)
                        return Response({
                            'status': "success",
                            "message": "news created sucessfully",
                            "data": NewsSerializer(news).data,
                        })
                    except:
                        return Response({
                            'status': "error",
                            "message": "error while creating news"
                        })
                except:
                    return Response({
                        "status": "error",
                        "message": f"category with id \'{id}\' does not exist"
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "invalid API token"
            })
        
    @action(detail=False,
            methods=['post'])
    def edit_news(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        id = int(request.POST.get('news_id'))
        title = request.POST.get('title')
        slug = slugify(title)
        post = request.POST.get('post')
        active = request.POST.get('active')
        verified = request.POST.get('verified')
        cat_id = int(request.POST.get('category_id'))
        
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                try:
                    category = NewsCategory.objects.get(id=cat_id)
                    try:
                        news = News.objects.get(id=id)
                        try:
                            news.title =title
                            news.slug = slug
                            news.post = post
                            news.active = active
                            news.verified = verified
                            news.category = category
                            news.save()
                            Log.objects.create(user=profile, action=f"edited a news post {title}")
                            return Response({
                                'status': "success",
                                "message": f"\'{news.title}\' edited sucessfully",
                                "data": NewsSerializer(news).data,
                            })
                        except:
                            return Response({
                                'status': "error",
                                "message": "error while saving news"
                            })
                    except:
                        return Response({
                            'status': "error",
                            "message": "invalid news id"
                        })
                except:
                    return Response({
                        "status": "error",
                        "message": f"category  with id \'{id}\' does not exist"
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "invalid API token"
            })
    @action(detail=False,
            methods=['post'])
    def delete_news(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        id = int(request.POST.get('id'))
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                try:
                    news = News.objects.get(id=id)
                    news.delete()
                    Log.objects.create(user=profile, action=f"deleted a news post {news.title}")
                    return Response({
                        'status': "success",
                        "message": f"news \'{news.title}\' deleted sucessfully",
                    })
                except:
                    return Response({
                        "status": "error",
                        "message": f"news with id \'{id}\' does not exist"
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })

class MeetingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    permission_classes = [AllowAny]
    @action(detail=False,
            methods=['get'])
    def get_meetings(self, request, *args, **kwargs):
        page = self.request.query_params.get('page')
        per_page = self.request.query_params.get('per_page')
        query = self.request.query_params.get('search')
        try:
            if page is None:
                page = 1
            else:
                page = int(page)
            if per_page is None:
                per_page = 20
            else:
                per_page = int(per_page)
            if query is None:
                query = ""
            start = (page - 1) * per_page
            stop = page * per_page
            total_items = Meeting.objects.filter(Q(title__icontains=query) |
                                                 Q(description__icontains=query)).count()
            total_pages = math.ceil(total_items/per_page)
            meetings = Meeting.objects.filter(Q(title__icontains=query) |
                                            Q(description__icontains=query))[start:stop]
            if meetings.exists():
                return Response({
                    'status': 'success',
                    'data': [MeetingSerializer(ne).data for ne in meetings],
                    'message': 'meeting list retrieved',
                    'page_number': page,
                    "list_per_page": per_page,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "search_query": query
                })
            else:
                return Response({
                    'status': 'success',
                    'message': 'No meeting found',
                    'page_number': page,
                    "list_per_page": per_page,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "search_query": query
                })
        except:
            return Response({
                'status': 'error',
                'message': 'Error getting meeting list'
            })
    @action(detail=False,
            methods=['get'])
    def get_meeting(self, request, *args, **kwargs):
        id = self.request.query_params.get('meeting_id')
        if id:
            try:
                meeting = Meeting.objects.get(id=int(id))
                if meeting is not None:
                    return Response({
                        'status': 'success',
                        'data': MeetingSerializer(meeting).data,
                        'message': 'meeting details retrieved'
                    })
                else:
                    return Response({
                        'status': 'success',
                        'message': 'Invalid meeting ID'
                    })
            except:
                return Response({
                    'status': 'error',
                    'message': 'Invalid meeting ID'
                })
        else:
            return Response({
                'status': 'success',
                'message': 'Invalid meeting ID'
            })
    @action(detail=False,
            methods=['post'])
    def create_meeting(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        title = request.POST.get('title')
        description = request.POST.get('description')
        ids = request.POST.get('members', [])
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                # check if position does not exist
                new_meet = Meeting.objects.create(title=title, description=description)
                new_meet.save()
                Log.objects.create(user=profile, action=f"created a new meeting {title}")
                create_action(profile, f"added a new meeting {title}", new_meet)
                members = Position.objects.filter(id__in=ids)
                for m in members:
                    new_meet.members.add(m)
                    new_meet.save()  
                return Response({
                    'status': "success",
                    "message": "meeting created sucessfully",
                    "data": MeetingSerializer(new_meet).data,
                })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })
    @action(detail=False,
            methods=['post'])
    def edit_meeting(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        title = request.POST.get('title')
        description = request.POST.get('description')
        mem_ids = request.POST.get('members', [])
        att_ids = request.POST.get('attended_by', [])
        id = int(request.POST.get('id'))
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                try:
                    meeting = Position.objects.get(id=id)
                    meeting.title = title
                    meeting.description = description
                    meeting.save()
                    Log.objects.create(user=profile, action=f"edited a meeting {title}")
                    members = Position.objects.filter(id__in=mem_ids)
                    for m in members:
                        if m not in meeting.members.all():
                            meeting.members.add(m)
                            meeting.save()
                    att_by = Position.objects.filter(id__in=att_ids)
                    for m in att_by:
                        if m not in meeting.attended_by.all():
                            meeting.attended_by.add(m)
                            meeting.save()
                    return Response({
                        'status': "success",
                        "message": "meeting edited sucessfully",
                        "data": MeetingSerializer(meeting).data,
                    })
                except:
                    return Response({
                        "status": "error",
                        "message": f"meeting with id \'{id}\' does not exist"
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })
    @action(detail=False,
            methods=['post'])
    def delete_meeting(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        id = int(request.POST.get('id'))
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                try:
                    meeting = Meeting.objects.get(id=id)
                    meeting.delete()
                    Log.objects.create(user=profile, action=f"deleted a meeting {meeting.title}")
                    return Response({
                        'status': "success",
                        "message": f"meeting \'{meeting.title}\' deleted sucessfully",
                    })
                except:
                    return Response({
                        "status": "error",
                        "message": f"meeting with id \'{id}\' does not exist"
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })

class EventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [AllowAny]
    permission_classes = [AllowAny]
    @action(detail=False,
            methods=['get'])
    def get_events(self, request, *args, **kwargs):
        page = self.request.query_params.get('page')
        per_page = self.request.query_params.get('per_page')
        query = self.request.query_params.get('search')
        try:
            if page is None:
                page = 1
            else:
                page = int(page)
            if per_page is None:
                per_page = 20
            else:
                per_page = int(per_page)
            if query is None:
                query = ""
            start = (page - 1) * per_page
            stop = page * per_page
            total_items = Event.objects.filter(Q(title__icontains=query) | Q(location__icontains=query) |
                                               Q(description__icontains=query)).count()
            total_pages = math.ceil(total_items/per_page)
            events = Event.objects.filter(Q(title__icontains=query) | Q(location__icontains=query) |
                                               Q(description__icontains=query))[start:stop]
            if events.exists():
                return Response({
                    'status': 'success',
                    'data': [EventSerializer(ne).data for ne in events],
                    'message': 'event list retrieved',
                    'page_number': page,
                    "list_per_page": per_page,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "search_query": query
                })
            else:
                return Response({
                    'status': 'success',
                    'message': 'No event found',
                    'page_number': page,
                    "list_per_page": per_page,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "search_query": query
                })
        except:
            return Response({
                'status': 'error',
                'message': 'Error getting event list'
            })
    @action(detail=False,
            methods=['get'])
    def get_event(self, request, *args, **kwargs):
        id = self.request.query_params.get('event_id')
        if id:
            try:
                event = Event.objects.get(id=int(id))
                if event is not None:
                    return Response({
                        'status': 'success',
                        'data': EventSerializer(event).data,
                        'message': 'event details retrieved'
                    })
                else:
                    return Response({
                        'status': 'success',
                        'message': 'Invalid event ID'
                    })
            except:
                return Response({
                    'status': 'error',
                    'message': 'Invalid event ID'
                })
        else:
            return Response({
                'status': 'success',
                'message': 'Invalid event ID'
            })
    @action(detail=False,
            methods=['post'])
    def create_event(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        title = request.POST.get('title')
        description = request.POST.get('description')
        date = request.POST.get('date')
        location = request.POST.get('location')
        link = request.POST.get('link')
        invitation = request.FILES.get('invitation')
        directions = request.POST.get('directions')
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                # check if position does not exist
                event = Event.objects.get(title=title)
                if event is not None:
                    return Response({
                        'status': "error",
                        "message": "event already exists!"
                    })
                else:
                    new_event = Event(organizer=profile, title=title, date=date,
                                      description=description, location=location,
                                      link=link, invitation=invitation, directions=directions)
                    new_event.save()
                    Log.objects.create(user=profile, action=f"created a new event {title}")
                    create_action(profile, f"added a new event {title}", new_event)
                    return Response({
                        'status': "success",
                        "message": "event created sucessfully",
                        "data": EventSerializer(new_event).data,
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })
    @action(detail=False,
            methods=['post'])
    def edit_event(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        title = request.POST.get('title')
        description = request.POST.get('description')
        date = request.POST.get('date')
        location = request.POST.get('location')
        link = request.POST.get('link')
        invitation = request.FILES.get('invitation')
        directions = request.POST.get('directions')
        id = int(request.POST.get('id'))
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                try:
                    event = Event.objects.get(id=id)
                    event.title = title
                    event.description=description
                    event.date = date
                    event.location = location
                    event.link = link
                    event.invitation = invitation
                    event.directions = directions
                    event.save()
                    Log.objects.create(user=profile, action=f"edited an event {event.title}")
                    return Response({
                        'status': "success",
                        "message": "event edited sucessfully",
                        "data": EventSerializer(event).data,
                    })
                except:
                    return Response({
                        "status": "error",
                        "message": f"event with id \'{id}\' does not exist"
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })
    @action(detail=False,
            methods=['post'])
    def delete_event(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        id = int(request.POST.get('id'))
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                try:
                    event = Event.objects.get(id=id)
                    event.delete()
                    Log.objects.create(user=profile, action=f"deleted an event {event.title}")
                    return Response({
                        'status': "success",
                        "message": f"event \'{event.title}\' deleted sucessfully",
                    })
                except:
                    return Response({
                        "status": "error",
                        "message": f"event with id \'{id}\' does not exist"
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })
    
class TaskViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [AllowAny]
    @action(detail=False,
            methods=['get'])
    def get_tasks(self, request, *args, **kwargs):
        page = self.request.query_params.get('page')
        per_page = self.request.query_params.get('per_page')
        completed = self.request.query_params.get('completed')
        query = self.request.query_params.get('search')
        try:
            if page is None:
                page = 1
            else:
                page = int(page)
            if per_page is None:
                per_page = 20
            else:
                per_page = int(per_page)
            if query is None:
                query = ""
            start = (page - 1) * per_page
            stop = page * per_page
            total_items = 0
            tasks = None
            com = None
            
            if completed is None:
                total_items = Task.objects.filter(Q(title__icontains=query) |
                                                Q(description__icontains=query)).count()
                tasks = Task.objects.filter(Q(title__icontains=query) |
                                                Q(description__icontains=query))[start:stop]
            else:
                if completed.lower() == 'true':
                    com = True
                elif completed.lower() == 'false':
                    com = False
                total_items = Task.objects.filter(completed=com).filter(Q(title__icontains=query) |
                                                  Q(description__icontains=query)).count()
                tasks = Task.objects.filter(completed=com).filter(Q(title__icontains=query) |
                                                  Q(description__icontains=query))[start:stop]
            total_pages = math.ceil(total_items/per_page)
            if tasks.exists():
                return Response({
                    'status': 'success',
                    'data': [TaskSerializer(ne).data for ne in tasks],
                    'message': 'task list retrieved',
                    'page_number': page,
                    "list_per_page": per_page,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "search_query": query
                })
            else:
                return Response({
                    'status': 'success',
                    'message': 'No task found',
                    'page_number': page,
                    "list_per_page": per_page,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "search_query": query
                })
        except:
            return Response({
                'status': 'error',
                'message': 'Error getting task list'
            })
    @action(detail=False,
            methods=['get'])
    def get_task(self, request, *args, **kwargs):
        id = self.request.query_params.get('task_id')
        if id:
            try:
                task = Task.objects.get(id=int(id))
                if task is not None:
                    return Response({
                        'status': 'success',
                        'data': TaskSerializer(task).data,
                        'message': 'task details retrieved'
                    })
                else:
                    return Response({
                        'status': 'success',
                        'message': 'Invalid task ID'
                    })
            except:
                return Response({
                    'status': 'error',
                    'message': 'Invalid task ID'
                })
        else:
            return Response({
                'status': 'success',
                'message': 'Invalid task ID'
            })
    @action(detail=False,
            methods=['post'])
    def create_task(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        title = request.POST.get('title')
        description = request.POST.get('description')
        deadline = request.POST.get('deadline')
        file = request.FILES.get('file')
        assigned_to_id = request.POST.get('employee_id')
        reward_id = request.POST.get('reward_id')
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                # check if position does not exist
                task = Task.objects.get(title=title)
                if task is not None:
                    return Response({
                        'status': "error",
                        "message": "task already exists!"
                    })
                else:
                    try:
                        reward = None
                        assigned_to = None
                        if reward_id:
                            reward = Reward.objects.get(id=int(reward_id))
                        if assigned_to_id:
                            assigned_to = Profile.objects.get(id_no=assigned_to_id)
                        try:
                            new_task = Task(created_by=profile, title=title, deadline=deadline,
                                            description=description, file=file, assigned_to=assigned_to,
                                            reward=reward)
                            new_task.save()
                            Log.objects.create(user=profile, action=f"created a new task {title}") 
                            return Response({
                                'status': "success",
                                "message": "task created sucessfully",
                                "data": TaskSerializer(new_task).data,
                            })
                        except:
                            return Response({
                                'status': "error",
                                "message": "Error while creating task"
                            })
                    except:
                        return Response({
                            'status': "error",
                            "message": "Invalid Reward/Employee id"
                        })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })
    @action(detail=False,
            methods=['post'])
    def edit_task(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        title = request.POST.get('title')
        description = request.POST.get('description')
        deadline = request.POST.get('deadline')
        file = request.FILES.get('file')
        assigned_to_id = request.POST.get('employee_id')
        reward_id = request.POST.get('reward_id')
        completed = request.POST.get('completed')
        id = int(request.POST.get('id'))
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                try:
                    task = Task.objects.get(id=id)
                    task.title = title
                    task.description = description
                    task.deadline = deadline
                    task.file = file
                    task.completed = completed
                    task.save()
                    Log.objects.create(user=profile, action=f"edited a task {task.title}")
                    reward = None
                    assigned_to = None
                    if reward_id:
                        reward = Reward.objects.get(id=int(reward_id))
                        task.reward = reward
                        task.save()
                    if assigned_to_id:
                        assigned_to = Profile.objects.get(id_no=assigned_to_id)
                        task.assigned_to = assigned_to
                    return Response({
                        'status': "success",
                        "message": "task edited sucessfully",
                        "data": TaskSerializer(task).data,
                    })
                except:
                    return Response({
                        "status": "error",
                        "message": f"task with id \'{id}\' does not exist"
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })
    @action(detail=False,
            methods=['post'])
    def delete_task(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        id = int(request.POST.get('id'))
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                try:
                    task = Task.objects.get(id=id)
                    task.delete()
                    Log.objects.create(user=profile, action=f"deleted a task {task.title}")
                    return Response({
                        'status': "success",
                        "message": f"task \'{task.title}\' deleted sucessfully",
                    })
                except:
                    return Response({
                        "status": "error",
                        "message": f"task with id \'{id}\' does not exist"
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })

class ComplaintViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    permission_classes = [AllowAny]
    @action(detail=False,
            methods=['get'])
    def get_complaints(self, request, *args, **kwargs):
        page = self.request.query_params.get('page')
        per_page = self.request.query_params.get('per_page')
        completed = self.request.query_params.get('addressed')
        query = self.request.query_params.get('search')
        try:
            if page is None:
                page = 1
            else:
                page = int(page)
            if per_page is None:
                per_page = 20
            else:
                per_page = int(per_page)
            if query is None:
                query = ""
            start = (page - 1) * per_page
            stop = page * per_page
            total_items = 0
            complaints = None
            com = None
            
            if completed is None:
                total_items = Complaint.objects.filter(title__icontains=query).count()
                complaints = Complaint.objects.filter(title__icontains=query)[start:stop]
            else:
                if completed.lower() == 'true':
                    com = True
                elif completed.lower() == 'false':
                    com = False
                total_items = Complaint.objects.filter(addressed=com).filter(title__icontains=query).count()
                complaints = Complaint.objects.filter(addressed=com).filter(title__icontains=query)[start:stop]
            total_pages = math.ceil(total_items/per_page)
            if complaints.exists():
                return Response({
                    'status': 'success',
                    'data': [ComplaintSerializer(ne).data for ne in complaints],
                    'message': 'complaint list retrieved',
                    'page_number': page,
                    "list_per_page": per_page,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "search_query": query
                })
            else:
                return Response({
                    'status': 'success',
                    'message': 'No complaint found',
                    'page_number': page,
                    "list_per_page": per_page,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "search_query": query
                })
        except:
            return Response({
                'status': 'error',
                'message': 'Error getting complaint list'
            })
    @action(detail=False,
            methods=['get'])
    def get_complaint(self, request, *args, **kwargs):
        id = self.request.query_params.get('complaint_id')
        if id:
            try:
                complaint = Complaint.objects.get(id=int(id))
                if complaint is not None:
                    return Response({
                        'status': 'success',
                        'data': ComplaintSerializer(complaint).data,
                        'message': 'complaint details retrieved'
                    })
                else:
                    return Response({
                        'status': 'success',
                        'message': 'Invalid complaint ID'
                    })
            except:
                return Response({
                    'status': 'error',
                    'message': 'Invalid complaint ID'
                })
        else:
            return Response({
                'status': 'success',
                'message': 'Invalid complaint ID'
            })
    @action(detail=False,
            methods=['post'])
    def edit_complaint(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        addressed = request.POST.get('addressed')
        solution = request.POST.get('solution')
        id = int(request.POST.get('id'))
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                try:
                    complaint = Complaint.objects.get(id=id)
                    complaint.addressed = addressed
                    complaint.solution = solution
                    complaint.save()
                    Log.objects.create(user=profile, action=f"edited complaint {complaint.title}")
                    return Response({
                        'status': "success",
                        "message": "complaint edited sucessfully",
                        "data": ComplaintSerializer(complaint).data,
                    })
                except:
                    return Response({
                        "status": "error",
                        "message": f"complaint with id \'{id}\' does not exist"
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })
    @action(detail=False,
            methods=['post'])
    def delete_complaint(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        id = int(request.POST.get('id'))
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                try:
                    complaint = Complaint.objects.get(id=id)
                    complaint.delete()
                    Log.objects.create(user=profile, action=f"deleted complaint {complaint.title}")
                    return Response({
                        'status': "success",
                        "message": f"complaint \'{complaint.title}\' deleted sucessfully",
                    })
                except:
                    return Response({
                        "status": "error",
                        "message": f"complaint with id \'{id}\' does not exist"
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })

class QueryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Query.objects.all()
    serializer_class = QuerySerializer
    permission_classes = [AllowAny]
    @action(detail=False,
            methods=['get'])
    def get_queries(self, request, *args, **kwargs):
        page = self.request.query_params.get('page')
        per_page = self.request.query_params.get('per_page')
        completed = self.request.query_params.get('addressed')
        query = self.request.query_params.get('search')
        try:
            if page is None:
                page = 1
            else:
                page = int(page)
            if per_page is None:
                per_page = 20
            else:
                per_page = int(per_page)
            if query is None:
                query = ""
            start = (page - 1) * per_page
            stop = page * per_page
            total_items = 0
            queries = None
            com = None
            
            if completed is None:
                total_items = Query.objects.filter(title__icontains=query).count()
                queries = Query.objects.filter(title__icontains=query)[start:stop]
            else:
                if completed.lower() == 'true':
                    com = True
                elif completed.lower() == 'false':
                    com = False
                total_items = Query.objects.filter(addressed=com).filter(title__icontains=query).count()
                queries = Query.objects.filter(addressed=com).filter(title__icontains=query)[start:stop]
            total_pages = math.ceil(total_items/per_page)
            if queries.exists():
                return Response({
                    'status': 'success',
                    'data': [QuerySerializer(ne).data for ne in queries],
                    'message': 'query list retrieved',
                    'page_number': page,
                    "list_per_page": per_page,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "search_query": query
                })
            else:
                return Response({
                    'status': 'success',
                    'message': 'No query found',
                    'page_number': page,
                    "list_per_page": per_page,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "search_query": query
                })
        except:
            return Response({
                'status': 'error',
                'message': 'Error getting query list'
            })
    @action(detail=False,
            methods=['get'])
    def get_query(self, request, *args, **kwargs):
        id = self.request.query_params.get('query_id')
        if id:
            try:
                query = Query.objects.get(id=int(id))
                if query is not None:
                    return Response({
                        'status': 'success',
                        'data': QuerySerializer(query).data,
                        'message': 'query details retrieved'
                    })
                else:
                    return Response({
                        'status': 'success',
                        'message': 'Invalid query ID'
                    })
            except:
                return Response({
                    'status': 'error',
                    'message': 'Invalid query ID'
                })
        else:
            return Response({
                'status': 'success',
                'message': 'Invalid query ID'
            })
    @action(detail=False,
            methods=['post'])
    def create_query(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        title = request.POST.get('title')
        query = request.POST.get('query')
        id = request.POST.get('employee_id')
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                # check if position does not exist
                try:
                    employee = Profile.objcts.get(id_no=id)
                    try:
                        new_q = Query(title=title, query=query, addressed_to=employee)
                        new_q.save()
                        Log.objects.create(user=profile, action=f"created a new query {new_q.title}")
                        return Response({
                            'status': "success",
                            "message": "query created sucessfully",
                            "data": QuerySerializer(new_q).data,
                        })
                    except:
                        return Response({
                            'status': "error",
                            "message": "Error creating query"
                        })
                except:
                    return Response({
                        'status': "error",
                        "message": "Invalid employee ID"
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })
    @action(detail=False,
            methods=['post'])
    def edit_query(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        addressed = request.POST.get('addressed')
        title = request.POST.get('title')
        q = request.POST.get('query')
        id_no = request.POST.get('employee_id')
        id = int(request.POST.get('id'))
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                try:
                    employee = Profile.objects.get(id_no=id_no)
                    query = Complaint.objects.get(id=id)
                    query.title = title
                    query.query = q
                    query.addressed = addressed
                    query.save()
                    Log.objects.create(user=profile, action=f"edited query {query.title}")
                    return Response({
                        'status': "success",
                        "message": "query edited sucessfully",
                        "data": QuerySerializer(query).data,
                    })
                except:
                    return Response({
                        "status": "error",
                        "message": f"Invalid query/employee ID"
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })
    @action(detail=False,
            methods=['post'])
    def delete_query(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        id = int(request.POST.get('id'))
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                try:
                    query = Query.objects.get(id=id)
                    query.delete()
                    Log.objects.create(user=profile, action=f"deleted query {query.title}")
                    return Response({
                        'status': "success",
                        "message": f"query \'{query.title}\' deleted sucessfully",
                    })
                except:
                    return Response({
                        "status": "error",
                        "message": f"query with id \'{id}\' does not exist"
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })

class LogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Log.objects.all()
    serializer_class = LogSerializer
    permission_classes = [AllowAny]
    @action(detail=False,
            methods=['get'])
    def get_logs(self, request, *args, **kwargs):
        page = self.request.query_params.get('page')
        per_page = self.request.query_params.get('per_page')
        id = self.request.query_params.get('employee_id')
        query = self.request.query_params.get('search')
        try:
            if page is None:
                page = 1
            else:
                page = int(page)
            if per_page is None:
                per_page = 20
            else:
                per_page = int(per_page)
            if query is None:
                query = ""
            start = (page - 1) * per_page
            stop = page * per_page
            total_items = 0
            logs = None
            employee = None
            
            if id is None:
                total_items = Log.objects.filter(action__icontains=query).count()
                logs = Log.objects.filter(action__icontains=query)[start:stop]
            else:
                employee = Profile.objects.get(id_no=id)
                total_items = Log.objects.filter(user=employee).filter(title__icontains=query).count()
                logs = Log.objects.filter(user=employee).filter(title__icontains=query)[start:stop]
            total_pages = math.ceil(total_items/per_page)
            if logs.exists():
                return Response({
                    'status': 'success',
                    'data': [LogSerializer(ne).data for ne in logs],
                    'message': 'log list retrieved',
                    'page_number': page,
                    "list_per_page": per_page,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "search_query": query
                })
            else:
                return Response({
                    'status': 'success',
                    'message': 'No log found',
                    'page_number': page,
                    "list_per_page": per_page,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "search_query": query
                })
        except:
            return Response({
                'status': 'error',
                'message': 'Error getting log list'
            })
    @action(detail=False,
            methods=['get'])
    def get_log(self, request, *args, **kwargs):
        id = self.request.query_params.get('log_id')
        if id:
            try:
                log = Log.objects.get(id=int(id))
                if log is not None:
                    return Response({
                        'status': 'success',
                        'data': LogSerializer(log).data,
                        'message': 'log details retrieved'
                    })
                else:
                    return Response({
                        'status': 'success',
                        'message': 'Invalid log ID'
                    })
            except:
                return Response({
                    'status': 'error',
                    'message': 'Invalid log ID'
                })
        else:
            return Response({
                'status': 'success',
                'message': 'Invalid log ID'
            })
    @action(detail=False,
            methods=['post'])
    def delete_log(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        id = int(request.POST.get('id'))
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                try:
                    log = Log.objects.get(id=id)
                    log.delete()
                    return Response({
                        'status': "success",
                        "message": f"log \'{log.action}\' deleted sucessfully",
                    })
                except:
                    return Response({
                        "status": "error",
                        "message": f"log with id \'{id}\' does not exist"
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })
    
class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny]
    @action(detail=False,
            methods=['get'])
    def get_notifications(self, request, *args, **kwargs):
        page = self.request.query_params.get('page')
        per_page = self.request.query_params.get('per_page')
        query = self.request.query_params.get('search')
        try:
            if page is None:
                page = 1
            else:
                page = int(page)
            if per_page is None:
                per_page = 20
            else:
                per_page = int(per_page)
            if query is None:
                query = ""
            start = (page - 1) * per_page
            stop = page * per_page
            
            total_items = Notification.objects.filter(verb__icontains=query).count()
            notifications = Notification.objects.filter(verb__icontains=query)[start:stop]
            total_pages = math.ceil(total_items/per_page)
            if notifications.exists():
                return Response({
                    'status': 'success',
                    'data': [NotificationSerializer(ne).data for ne in notifications],
                    'message': 'notification list retrieved',
                    'page_number': page,
                    "list_per_page": per_page,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "search_query": query
                })
            else:
                return Response({
                    'status': 'success',
                    'message': 'No notification found',
                    'page_number': page,
                    "list_per_page": per_page,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "search_query": query
                })
        except:
            return Response({
                'status': 'error',
                'message': 'Error getting notification list'
            })
    @action(detail=False,
            methods=['get'])
    def get_notification(self, request, *args, **kwargs):
        id = self.request.query_params.get('notification_id')
        if id:
            try:
                notification = Notification.objects.get(id=int(id))
                if notification is not None:
                    return Response({
                        'status': 'success',
                        'data': NotificationSerializer(notification).data,
                        'message': 'notification details retrieved'
                    })
                else:
                    return Response({
                        'status': 'success',
                        'message': 'Invalid notification ID'
                    })
            except:
                return Response({
                    'status': 'error',
                    'message': 'Invalid notification ID'
                })
        else:
            return Response({
                'status': 'success',
                'message': 'Invalid notification ID'
            })
    @action(detail=False,
            methods=['post'])
    def delete_notification(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        id = int(request.POST.get('id'))
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                try:
                    notification = Notification.objects.get(id=id)
                    notification.delete()
                    Log.objects.create(user=profile, action=f"deleted notification {notification.title}")
                    return Response({
                        'status': "success",
                        "message": f"notification \'{notification.verb}\' deleted sucessfully",
                    })
                except:
                    return Response({
                        "status": "error",
                        "message": f"notification with id \'{id}\' does not exist"
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })

class RewardViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Reward.objects.all()
    serializer_class = RewardSerializer
    permission_classes = [AllowAny]
    @action(detail=False,
            methods=['get'])
    def get_rewards(self, request, *args, **kwargs):
        page = self.request.query_params.get('page')
        per_page = self.request.query_params.get('per_page')
        query = self.request.query_params.get('search')
        try:
            if page is None:
                page = 1
            else:
                page = int(page)
            if per_page is None:
                per_page = 20
            else:
                per_page = int(per_page)
            if query is None:
                query = ""
            start = (page - 1) * per_page
            stop = page * per_page
            total_items = Reward.objects.filter(title__icontains=query).count()
            total_pages = math.ceil(total_items/per_page)
            rewards = Reward.objects.filter(title__icontains=query)[start:stop]
            if rewards.exists():
                return Response({
                    'status': 'success',
                    'data': [RewardSerializer(pos).data for pos in rewards],
                    'message': 'reward list retrieved',
                    'page_number': page,
                    "list_per_page": per_page,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "search_query": query
                })
            else:
                return Response({
                    'status': 'success',
                    'message': 'No reward found',
                    'page_number': page,
                    "list_per_page": per_page,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "search_query": query
                })
        except:
            return Response({
                'status': 'error',
                'message': 'Error getting reward list'
            })
    @action(detail=False,
            methods=['get'])
    def get_reward(self, request, *args, **kwargs):
        id = self.request.query_params.get('reward_id')
        if id:
            try:
                reward = Reward.objects.get(id=int(id))
                if reward is not None:
                    return Response({
                        'status': 'success',
                        'data': RewardSerializer(reward).data,
                        'message': 'reward details retrieved'
                    })
                else:
                    return Response({
                        'status': 'success',
                        'message': 'Invalid reward ID'
                    })
            except:
                return Response({
                    'status': 'error',
                    'message': 'Invalid reward ID'
                })
        else:
            return Response({
                'status': 'success',
                'message': 'Invalid reward ID'
            })
    @action(detail=False,
            methods=['post'])
    def create_reward(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        title = request.POST.get('title')
        description = request.POST.get('description')
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                # check if position does not exist
                reward = Reward.objects.get(title=title)
                if reward is not None:
                    return Response({
                        'status': "error",
                        "message": "reward already exists!"
                    })
                else:
                    new_pos = reward(title=title, description=description)
                    new_pos.save()
                    Log.objects.create(user=profile, action=f"created a new reward {title}")
                    return Response({
                        'status': "success",
                        "message": "reward created sucessfully",
                        "data": RewardSerializer(new_pos).data,
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })
    @action(detail=False,
            methods=['post'])
    def edit_reward(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        title = request.POST.get('title')
        description = request.POST.get('description')
        id = int(request.POST.get('id'))
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                try:
                    reward = Reward.objects.get(id=id)
                    reward.title = title
                    reward.description = description
                    reward.save()
                    Log.objects.create(user=profile, action=f"edited reward {reward.title}")
                    return Response({
                        'status': "success",
                        "message": "reward edited sucessfully",
                        "data": RewardSerializer(reward).data,
                    })
                except:
                    return Response({
                        "status": "error",
                        "message": f"reward with id \'{id}\' does not exist"
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })
    @action(detail=False,
            methods=['post'])
    def delete_reward(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        id = int(request.POST.get('id'))
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                try:
                    reward = Reward.objects.get(id=id)
                    reward.delete()
                    Log.objects.create(user=profile, action=f"deleted reward {reward.title}")
                    return Response({
                        'status': "success",
                        "message": f"reward \'{reward.title}\' deleted sucessfully",
                    })
                except:
                    return Response({
                        "status": "error",
                        "message": f"reward with id \'{id}\' does not exist"
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })

class BankAccountViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer
    permission_classes = [AllowAny]
    @action(detail=False,
            methods=['get'])
    def get_bank_accounts(self, request, *args, **kwargs):
        page = self.request.query_params.get('page')
        per_page = self.request.query_params.get('per_page')
        query = self.request.query_params.get('search')
        try:
            if page is None:
                page = 1
            else:
                page = int(page)
            if per_page is None:
                per_page = 20
            else:
                per_page = int(per_page)
            if query is None:
                query = ""
            start = (page - 1) * per_page
            stop = page * per_page
            
            total_items = BankAccount.objects.filter(Q(account_name__icontains=query) | Q(account_number__icontains=query) |
                                                     Q(bank__bank_name__icontains=query)).count()
            bank_accounts = BankAccount.objects.filter(Q(account_name__icontains=query) | Q(account_number__icontains=query) |
                                                     Q(bank__bank_name__icontains=query))[start:stop]
            total_pages = math.ceil(total_items/per_page)
            if bank_accounts.exists():
                return Response({
                    'status': 'success',
                    'data': [BankAccountSerializer(ne).data for ne in bank_accounts],
                    'message': 'bank account list retrieved',
                    'page_number': page,
                    "list_per_page": per_page,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "search_query": query
                })
            else:
                return Response({
                    'status': 'success',
                    'message': 'No bank account found',
                    'page_number': page,
                    "list_per_page": per_page,
                    "total_pages": total_pages,
                    "total_items": total_items,
                    "search_query": query
                })
        except:
            return Response({
                'status': 'error',
                'message': 'Error getting bank account list'
            })
    @action(detail=False,
            methods=['get'])
    def get_bank_account(self, request, *args, **kwargs):
        id = self.request.query_params.get('bank_account_id')
        if id:
            try:
                bank_account = BankAccount.objects.get(id=int(id))
                if bank_account is not None:
                    return Response({
                        'status': 'success',
                        'data': BankAccountSerializer(bank_account).data,
                        'message': 'bank account details retrieved'
                    })
                else:
                    return Response({
                        'status': 'success',
                        'message': 'Invalid bank account ID'
                    })
            except:
                return Response({
                    'status': 'error',
                    'message': 'Invalid bank account ID'
                })
        else:
            return Response({
                'status': 'success',
                'message': 'Invalid bank account ID'
            })
    @action(detail=False,
            methods=['post'])
    def delete_bank_account(self, request, *args, **kwargs):
        key = request.POST.get('api_token')
        id = int(request.POST.get('id'))
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                try:
                    bank_account = BankAccount.objects.get(id=id)
                    bank_account.delete()
                    Log.objects.create(user=profile, action=f"deleted bank account {bank_account.account_name}({bank_account.account_number})")
                    return Response({
                        'status': "success",
                        "message": f"bank account \'{bank_account.account_name}({bank_account.account_number})\' deleted sucessfully",
                    })
                except:
                    return Response({
                        "status": "error",
                        "message": f"bank account with id \'{id}\' does not exist"
                    })
            else:
                return Response({
                    'status': "error",
                    "message": "User is not authorized"
                })
        except:
            return Response({
                'status': "error",
                "message": "Invalid API token"
            })

class GroupChatViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GroupChat.objects.all()
    serializer_class = GroupChatSerializer
    permission_classes = [AllowAny]
    @action(detail=False,
            methods=['get'])
    def get_group_chats(self, request, *args, **kwargs):
        try:
            group_chats = GroupChat.objects.all()
            if group_chats.exists():
                return Response({
                    'status': 'success',
                    'data': [GroupChatSerializer(ne).data for ne in group_chats],
                    'message': 'group chat list retrieved'
                })
            else:
                return Response({
                    'status': 'success',
                    'message': 'No group chat found'
                })
        except:
            return Response({
                'status': 'error',
                'message': 'Error getting group chat list'
            })
    @action(detail=False,
            methods=['get'])
    def get_group_chat(self, request, *args, **kwargs):
        id = self.request.query_params.get('group_chat_id')
        if id:
            try:
                group_chat = GroupChat.objects.get(id=int(id))
                if group_chat is not None:
                    return Response({
                        'status': 'success',
                        'data': GroupChatSerializer(group_chat).data,
                        'message': 'group chat details retrieved'
                    })
                else:
                    return Response({
                        'status': 'success',
                        'message': 'Invalid group_chat ID'
                    })
            except:
                return Response({
                    'status': 'error',
                    'message': 'Invalid group chat ID'
                })
        else:
            return Response({
                'status': 'success',
                'message': 'Invalid group chat ID'
            })
    @action(detail=False,
            methods=['get'])
    def get_group_members(self, request, *args, **kwargs):
        id = self.request.query_params.get('group_chat_id')
        if id:
            try:
                group_chat = GroupChat.objects.get(id=int(id))
                if group_chat is not None:
                    members = group_chat.members.all()
                    return Response({
                        'status': 'success',
                        'data': [EmployeeSerializer(mem).data for mem in members],
                        'message': 'members list retrieved'
                    })
                else:
                    return Response({
                        'status': 'success',
                        'message': 'Invalid group_chat ID'
                    })
            except:
                return Response({
                    'status': 'error',
                    'message': 'Invalid group chat ID'
                })
        else:
            return Response({
                'status': 'success',
                'message': 'Invalid group chat ID'
            })
    @action(detail=False,
            methods=['get'])
    def get_chats(self, request, *args, **kwargs):
        id = self.request.query_params.get('group_chat_id')
        if id:
            try:
                group_chat = GroupChat.objects.get(id=int(id))
                if group_chat is not None:
                    chats = group_chat.chat_messages.all()
                    return Response({
                        'status': 'success',
                        'data': [ChatMessageSerializer(chat).data for chat in chats],
                        'message': 'chat messages retrieved'
                    })
                else:
                    return Response({
                        'status': 'success',
                        'message': 'Invalid group chat ID'
                    })
            except:
                return Response({
                    'status': 'error',
                    'message': 'Invalid group chat ID'
                })
        else:
            return Response({
                'status': 'success',
                'message': 'Invalid group chat ID'
            })

