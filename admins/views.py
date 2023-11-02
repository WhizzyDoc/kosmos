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
            methods=['post'],
            authentication_classes = [BasicAuthentication])
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
            authentication_classes = [BasicAuthentication])
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
        a_type = request.data.get('account_type')
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
                    if a_type == 'admin':
                        new_user.groups.add(admin_group)
                        new_user.is_superuser = True
                        new_user.save()
                    elif a_type == 'staff':
                        new_user.groups.add(staff_group)
                        new_user.save()
                    elif a_type == 'employee':
                        new_user.groups.add(employee_group)
                        new_user.save()
                    # creates a new API key for user instance
                    api_key = generate_token()
                    # create a new profile
                    new_profile = Profile(user=new_user, email=email, id_no=id_no, first_name=f_name, last_name=l_name, api_token=api_key)
                    new_profile.save()
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

    # to register the created account by filling profile details
    @action(detail=False,
            methods=['post'])
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
        image = request.FILES.get('image')
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
                
                
    @action(detail=False,
            methods=['post'])
    def authentication(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                if admin_group in user.groups.all():
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
            methods=['post'])
    def get_admin_profile(self, request, *args, **kwargs):
        key = request.data.get('api_token')
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
                "message": "profile not found"
            })
    @action(detail=False,
            methods=['post'])
    def edit_admin_profile(self, request, *args, **kwargs):
        key = request.data.get('api_token')
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                # edited attributes
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
    @action(detail=False,
            methods=['post'])
    def create_position(self, request, *args, **kwargs):
        key = request.data.get('api_token')
        title = request.data.get('title')
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
                    new_pos = Position.objects.create(title=title)  
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
                "message": "profile not found"
            })
    @action(detail=False,
            methods=['post'])
    def edit_position(self, request, *args, **kwargs):
        key = request.data.get('api_token')
        title = request.data.get('title')
        id = int(request.data.get('id'))
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                try:
                    position = Position.objects.get(id=id)
                    position.title = title
                    position.save()
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
                "message": "profile not found"
            })
    @action(detail=False,
            methods=['post'])
    def delete_position(self, request, *args, **kwargs):
        key = request.data.get('api_token')
        id = int(request.data.get('id'))
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                try:
                    position = Position.objects.get(id=id)
                    position.delete()
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
                "message": "profile not found"
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
    @action(detail=False,
            methods=['post'])
    def create_department(self, request, *args, **kwargs):
        key = request.data.get('api_token')
        title = request.data.get('title')
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
                    new_dep = Department.objects.create(title=title)  
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
                "message": "profile not found"
            })
    @action(detail=False,
            methods=['post'])
    def edit_department(self, request, *args, **kwargs):
        key = request.data.get('api_token')
        title = request.data.get('title')
        id = int(request.data.get('id'))
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                try:
                    department = Department.objects.get(id=id)
                    department.title = title
                    department.save()
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
                "message": "profile not found"
            })
    @action(detail=False,
            methods=['post'])
    def delete_department(self, request, *args, **kwargs):
        key = request.data.get('api_token')
        id = int(request.data.get('id'))
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                try:
                    department = Department.objects.get(id=id)
                    department.delete()
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
                "message": "profile not found"
            })

class BankViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Bank.objects.all()
    serializer_class = BankSerializer
    permission_classes = [AllowAny]
    # to get all banks to includ in registration form data
    @action(detail=False,
            methods=['get'])
    def get_banks(self, request, *args, **kwargs):
        try:
            banks = Bank.objects.all()
            if banks.exists():
                return Response({
                    'status': 'success',
                    'data': [BankSerializer(bank).data for bank in banks],
                    'message': 'bank list retrieved'
                })
            else:
                return Response({
                    'status': 'success',
                    'message': 'No bank found'
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
        key = request.data.get('api_token')
        name = request.data.get('bank_name')
        code = request.data.get('bank_code')
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
                    new_bank = Bank.objects.create(bank_name=name, bank_code=code)  
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
        key = request.data.get('api_token')
        name = request.data.get('bank_name')
        code = request.data.get('bank_code')
        id = int(request.data.get('id'))
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
        key = request.data.get('api_token')
        id = int(request.data.get('id'))
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                try:
                    bank = Bank.objects.get(id=id)
                    bank.delete()
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
        try:
            categories = NewsCategory.objects.all()
            if categories.exists():
                return Response({
                    'status': 'success',
                    'data': [NewsCategorySerializer(cat).data for cat in categories],
                    'message': 'category list retrieved'
                })
            else:
                return Response({
                    'status': 'success',
                    'message': 'No categories found'
                })
        except:
            return Response({
                'status': 'error',
                'message': 'Error getting categories list'
            })
    @action(detail=False,
            methods=['post'])
    def create_category(self, request, *args, **kwargs):
        key = request.data.get('api_token')
        title = request.data.get('title')
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
                    new_cat = NewsCategory.objects.create(title=title, slug=slug)  
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
                "message": "profile not found"
            })
    @action(detail=False,
            methods=['post'])
    def edit_category(self, request, *args, **kwargs):
        key = request.data.get('api_token')
        title = request.data.get('title')
        slug = slugify(title)
        id = int(request.data.get('id'))
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                try:
                    category = NewsCategory.objects.get(id=id)
                    category.title = title
                    category.slug = slug
                    category.save()
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
                "message": "profile not found"
            })
    @action(detail=False,
            methods=['post'])
    def delete_category(self, request, *args, **kwargs):
        key = request.data.get('api_token')
        id = int(request.data.get('id'))
        try:
            profile = Profile.objects.get(api_token=key)
            user = profile.user
            if admin_group in user.groups.all():
                try:
                    category = NewsCategory.objects.get(id=id)
                    category.delete()
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
                "message": "profile not found"
            })