from rest_framework import serializers
from .models import *
from main.models import *
from django.contrib.auth.models import User

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


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    position = PositionSerializer(many=False, read_only=True)
    department = DepartmentSerializer(many=False, read_only=True)
    class Meta:
        model = Profile
        fields = ['id', 'user','title', 'first_name', 'middle_name', 'last_name', 'email', 'phone_number', 'date_of_birth',
                  'address', 'appointment_date', 'position', 'department', 'id_no', 'salary', 'is_premium_user', 'image',
                  'api_token']

        
class EventSerializer(serializers.ModelSerializer):
    organizer = ProfileSerializer(many=False, read_only=True)
    invitees = ProfileSerializer(many=True, read_only=True)
    attending = ProfileSerializer(many=True, read_only=True)
    class Meta:
        model = Event
        fields = ['id', 'organizer', 'title', 'description', 'date', 'type', 'location', 'link', 'invitation', 'directions',
                  'invitees', 'attending']

class MeetingSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(many=False, read_only=True)
    members = PositionSerializer(many=True, read_only=True)
    attended_by = PositionSerializer(many=True, read_only=True)
    class Meta:
        model = Meeting
        fields = ['id', 'title', 'description', 'date', 'departments', 'members', 'attended_by']

class NewsSerializer(serializers.ModelSerializer):
    author = ProfileSerializer(many=False, read_only=True)
    category = NewsCategorySerializer(many=False, read_only=True)
    class Meta:
        model = News
        fields = ['id', 'author', 'title', 'slug', 'category', 'date', 'active', 'verified', 'post']

class RewardSerializer(serializers.ModelSerializer):
    owner = ProfileSerializer(many=False, read_only=True)
    class Meta:
        model = Reward
        fields = ['id', 'owner', 'description']

class TaskSerializer(serializers.ModelSerializer):
    created_by = ProfileSerializer(many=False, read_only=True)
    reward = RewardSerializer(many=False, read_only=True)
    assigned_to = ProfileSerializer(many=True, read_only=True)
    completed_by = ProfileSerializer(many=True, read_only=True)
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'created_by', 'file', 'type', 'reward', 'assigned_to',
                  'completed', 'completed_by']