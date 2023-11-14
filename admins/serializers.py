from rest_framework import serializers
from .models import *
from main.models import *
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = ['title', 'tagline', 'company_email', 'logo', 'about', 'objectives', 'mission', 'last_modified']

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


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    position = PositionSerializer(many=False, read_only=True)
    department = DepartmentSerializer(many=False, read_only=True)
    class Meta:
        model = Profile
        fields = ['id', 'user','title', 'first_name', 'middle_name', 'last_name', 'email', 'phone_number', 'date_of_birth',
                  'address', 'appointment_date', 'position', 'department', 'id_no', 'salary', 'is_premium_user', 'image',
                  'api_token', 'city', 'state', 'nationality']

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'id_no', 'first_name', 'last_name', 'email', 'image']

class BankAccountSerializer(serializers.ModelSerializer):
    user = EmployeeSerializer(many=False, read_only=True)
    bank = BankSerializer(many=False, read_only=True)
    class Meta:
        model = BankAccount
        fields = ['id', 'user', 'bank', 'account_number', 'account_name']
        
class EventSerializer(serializers.ModelSerializer):
    organizer = ProfileSerializer(many=False, read_only=True)
    class Meta:
        model = Event
        fields = ['id', 'organizer', 'title', 'description', 'date', 'location', 'link', 'invitation', 'directions']

class MeetingSerializer(serializers.ModelSerializer):
    departments = DepartmentSerializer(many=True, read_only=True)
    members = PositionSerializer(many=True, read_only=True)
    attended_by = PositionSerializer(many=True, read_only=True)
    class Meta:
        model = Meeting
        fields = ['id', 'title', 'description', 'date', 'departments', 'members', 'attended_by']

class NewsSerializer(serializers.ModelSerializer):
    author = EmployeeSerializer(many=False, read_only=True)
    category = NewsCategorySerializer(many=False, read_only=True)
    class Meta:
        model = News
        fields = ['id', 'author', 'title', 'slug', 'category', 'date', 'active', 'verified', 'post']

class RewardSerializer(serializers.ModelSerializer):
    owner = ProfileSerializer(many=False, read_only=True)
    class Meta:
        model = Reward
        fields = ['id', 'title', 'description']

class TaskSerializer(serializers.ModelSerializer):
    reward = RewardSerializer(many=False, read_only=True)
    assigned_to = EmployeeSerializer(many=False, read_only=True)
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'file', 'reward', 'assigned_to',
                  'completed', 'deadline']

class LogSerializer(serializers.ModelSerializer):
    user = EmployeeSerializer(many=False, read_only=True)
    class Meta:
        model = Log
        fields = ['id', 'user', 'action', 'date']

class NotificationSerializer(serializers.ModelSerializer):
    user = EmployeeSerializer(many=False, read_only=True)
    target_ct = serializers.SerializerMethodField()
    class Meta:
        model = Notification
        fields = ['id', 'user', 'verb', 'target_ct', 'created']
    
    def get_target_ct(self, obj):
        return obj.target_ct.model
    
    """
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['target_type'] = self.get_target_type(instance)
        ret['target'] = serializers.ModelSerializer(instance.target_ct.model_class()).to_representation(instance.target)
        return ret
    """
class ComplaintSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(many=False, read_only=True)
    class Meta:
        model = Complaint
        fields = ['id', 'title', 'complaint', 'proposed_solution', 'addressed', 'solution',
                  'date', 'employee']

class QuerySerializer(serializers.ModelSerializer):
    addressed_to = EmployeeSerializer(many=False, read_only=True)
    class Meta:
        model = Query
        fields = ['id', 'title', 'query', 'addressed_to', 'addressed']

class GroupChatSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(many=False, read_only=True)
    members = EmployeeSerializer(many=True, read_only=True)
    class Meta:
        model = GroupChat
        fields = ['id', 'title', 'department', 'members', 'created']

class ChatMessageSerializer(serializers.ModelSerializer):
    group = GroupChatSerializer(many=False, read_only=True)
    sender = EmployeeSerializer(many=False, read_only=True)
    seen_by = EmployeeSerializer(many=True, read_only=True)
    class Meta:
        model = ChatMessage
        fields = ['id', 'group', 'sender', 'message', 'date', 'seen_by']