from rest_framework import generics, viewsets
from .models import *
from main.models import *
from employee.models import *
from .serializers import *
from .bank import bank_list
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from rest_framework.decorators import action
from django.contrib.auth import login, authenticate, logout
import re
import json
from django.db.models import Q
from .encrypt_utils import encrypt, decrypt
from datetime import datetime, timedelta
from django.utils import timezone
from django.http import FileResponse
from django.utils.text import slugify
import random
import string
from rest_framework.authtoken.models import Token

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

def generate(n):
    digits = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
    random_combination = ''.join(random.choice(digits) for _ in range(n))
    return random_combination

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
            methods=['post'],
            authentication_classes = [TokenAuthentication])
    def create_site_info(self, request, *args, **kwargs):
        if request.method == 'POST':
            title = request.data.get('title')
            tagline = request.data.get('tagline')
            about = request.data.get('about')
            objectives = request.data.get('objectives')
            mission = request.data.get('mission')
            logo = None
            if request.FILES:
                logo = request.FILES.get('logo')
            try:
                sites = Site.objects.all()
                if sites.exists():
                    for s in sites:
                        s.delete()
                new_site = Site(title=title, tagline=tagline, logo=logo, about=about, objectives=objectives, mission=mission)
                new_site.save()
                return Response({
                    'status': 'success',
                    'message': 'site info created sucessfully',
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
                'message': 'GET method not allowed'
            })
    @action(detail=False,
            methods=['post'],
            authentication_classes = [TokenAuthentication])
    def edit_site_info(self, request, *args, **kwargs):
        if request.method == 'POST':
            title = request.data.get('title')
            tagline = request.data.get('tagline')
            about = request.data.get('about')
            objectives = request.data.get('objectives')
            mission = request.data.get('mission')
            logo = request.FILES.get('logo')
            try:
                sites = Site.objects.all()
                if sites.exists():
                    site = Site.objects.first()
                    if title:
                        site.title = title
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
                'message': 'GET method not allowed'
            })
            
class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]
    @action(detail=False,
            methods=['post'])
    def create_account(self, request, *args, **kwargs):
        email = request.data.get('email')
        f_name = request.data.get('first_name')
        l_name = request.data.get('last_name')
        type = (request.data.get('account_type')).strip()
        # check if email is valid (view.py line 49)
        if is_valid_email(email):
            emails = []
            users = User.objects.all()
            # get a list of all registered emails
            for user in users:
                emails.append(user.email)
            # check if email is not in existence
            if email not in emails:
                group = None
                # check account type and retrieve appropriate group
                if type == 'admin':
                    group = Group.objects.get(name="admin")
                elif type == 'employee':
                    group = Group.objects.get(name="employee")
                try:  
                    new_user = User.objects.create(username=email, email=email, first_name=f_name, last_name=l_name)
                    new_user.set_password(l_name)
                    new_user.save()
                    new_user.groups.add(group)
                    # creates a new API key for user instance
                    token = Token.objects.create(user=new_user)
                    # create a new profile
                    new_profile = Profile.objects.create(user=new_user, api_token=token, email=email, first_name=f_name, last_name=l_name)
                    # create a new bank account model
                    BankAccount.objects.create(user=new_profile)
                    return Response({
                        'status': 'success',
                        'message': f'Account created successfully. username is {email} and password is {f_name}',
                        'profile': ProfileSerializer(new_profile).data
                    })
                except:
                    return Response({
                        'status': 'error',
                        'message': f'Error occued while creating account',
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

    # to register the created account by filling profile details
    @action(detail=False,
            methods=['post'],
            authentication_classes = [TokenAuthentication])
    def register(self, request, *args, **kwargs):
        email = request.data.get('email')
        title = request.data.get('title')
        m_name = request.data.get('middle_name')
        dob = request.data.get('date_of_birth')
        a_date = request.data.get('appointment_date')
        address = request.data.get('address')
        nationality = request.data.get('nationality')
        phone_number = request.data.get('phone_number')
        position = request.data.get('position')
        department = request.data.get('department')
        salary = request.data.get('salary')
        #id_no = ''
        # check if post email data is valid
        if is_valid_email(email):
            profile = Profile.objects.get(email=email)
            if profile is not None:
                # get the position and department models from their given id
                if position is not None and str(position) != '':
                    try:
                        p = Position.objects.get(id=int(position))
                        profile.position = p
                        profile.save()
                    except:
                        return Response({
                            'status': 'error',
                            'message': 'Invalid id for position'
                        })
                if department is not None and str(department) != '':
                    try:
                        d = Department.objects.get(id=int(department))
                        profile.department = d
                        profile.save()
                    except:
                        return Response({
                            'status': 'error',
                            'message': 'Invalid id for department'
                        })
                profile.title = title
                profile.date_of_birth = dob
                profile.middle_name = m_name
                profile.appointment_date = a_date
                profile.address = address
                profile.nationality = nationality
                profile.phone_number = phone_number
                profile.salary = salary
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
                
                
    @action(detail=False,
            methods=['post'])
    def authentication(self, request, *args, **kwargs):
        username = sterilize(request.data.get('username'))
        password = request.data.get('password').strip()
        group = Group.objects.get(name="admin")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                if group in user.groups.all():
                    login(request, user)
                    profile = get_object_or_404(Profile, user=user)
                    return Response({
                        'status': "success",
                        "message": "login successful",
                        "profile": ProfileSerializer(profile).data,
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
            methods=['post'],
            authentication_classes = [TokenAuthentication])
    def get_admin_profile(self, request, *args, **kwargs):
        key = request.POST.get('api_token').strip()
        token = Token.objects.get(key=key)
        group = Group.objects.get(name="admin")
        try:
            profile = Profile.objects.get(api_token=token)
            user = profile.user
            if group in user.groups.all():
                return Response({
                    'status': "success",
                    "message": "data fetched successfully",
                    "profile": ProfileSerializer(profile).data,
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

class PositionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = [AllowAny]
    # to get all positions to includ in registration form data
    @action(detail=False,
            methods=['get'])
    def get_positions(self, request, *args, **kwargs):
        try:
            positions = Position.objects.all()
            if positions.exists():
                return Response({
                    'status': 'success',
                    'data': [PositionSerializer(pos).data for pos in positions],
                    'message': 'position list retrieved'
                })
            else:
                return Response({
                    'status': 'success',
                    'message': 'No position found'
                })
        except:
            return Response({
                'status': 'error',
                'message': 'Error getting position list'
            })

class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [AllowAny]
    # to get all departments to include in registration form data
    @action(detail=False,
            methods=['get'])
    def get_departments(self, request, *args, **kwargs):
        try:
            departments = Department.objects.all()
            if departments.exists():
                return Response({
                    'status': 'success',
                    'data': [DepartmentSerializer(dept).data for dept in departments],
                    'message': 'department list retrieved'
                })
            else:
                return Response({
                    'status': 'success',
                    'message': 'No department found'
                })
        except:
            return Response({
                'status': 'error',
                'message': 'Error getting department list'
            })
    