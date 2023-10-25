from rest_framework import serializers
from .models import *
from main.models import *
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_superuser', 'is_active']

class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = ['title', 'tagline', 'logo', 'about', 'objectives', 'mission', 'last_modified']

class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ['id', 'title']
        
class NewsCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsCategory
        fields = ['id', 'title', 'slug']

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'title']
        
class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = ['id', 'bank_name', 'bank_code']

class BankAccountSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    bank = BankSerializer(many=False, read_only=True)
    class Meta:
        model = BankAccount
        fields = ['id', 'user', 'bank', 'account_number', 'account_name']

class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = ['key']

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    position = PositionSerializer(many=False, read_only=True)
    api_token = TokenSerializer(many=False, read_only=True)
    department = DepartmentSerializer(many=False, read_only=True)
    class Meta:
        model = Profile
        fields = ['id', 'user','title', 'first_name', 'middle_name', 'last_name', 'email', 'phone_number', 'date_of_birth',
                  'address', 'appointment_date', 'position', 'department', 'id_no', 'salary', 'is_premium_user',
                  'api_token']

        
class EventSerializer(serializers.ModelSerializer):
    organizer = ProfileSerializer(many=False, read_only=True)
    class Meta:
        model = Event
        fields = ['id', 'organizer', 'title', 'description', 'date', 'type', 'location', 'link', 'directions']

class NewsSerializer(serializers.ModelSerializer):
    author = ProfileSerializer(many=False, read_only=True)
    category = NewsCategorySerializer(many=False, read_only=True)
    class Meta:
        model = News
        fields = ['id', 'author', 'title', 'slug', 'category', 'date', 'active', 'verified', 'post']

class RewardsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rewards
        fields = ['id', 'name', 'reward_type']