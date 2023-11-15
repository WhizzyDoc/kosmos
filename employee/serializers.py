import re
from rest_framework.serializers import ModelSerializer
from main.models import *
from rest_framework.validators import ValidationError
from rest_framework import serializers
from admins.models import *


class DepartmentSerializer(ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"

class PositionSerializer(ModelSerializer):
    class Meta:
        model = Position
        fields = "__all__"


class ProfileSerializer(ModelSerializer):
    department = DepartmentSerializer()
    position = PositionSerializer()
    class Meta:
        model = Profile
        exclude = ["user", "api_token"]
        # fields = "__all__"
        read_only_fields = Profile._meta.get_fields()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["department"] = data["department"]["title"]
        data["position"] = data["position"]["title"]

        return data



class BankAccountSerializer(ModelSerializer):
    class Meta:
        model = BankAccount
        fields = "__all__"

    def validate_account_number(self, value):
        if not value.isdigit():
            raise ValidationError("Account number can only contain numbers!")
        return value


    def validate_account_name(self, value):
        def contains_number(s):
            return any(char.isdigit() for char in s)

        if contains_number(value):
            raise ValidationError("Name can only be texts")
        return value

    def validate_bank(self, value):
        if value == None:
            raise ValidationError("Invalid bank name")
        return value

class BankAccountUpdateSerializer(ModelSerializer):
    class Meta:
        model = BankAccount
        exclude = ["user"]


    def validate_api_key(self, value):
        # Retrieve the associated Profile based on the provided api_key
        try:
            profile = Profile.objects.get(api_key=value)
        except Profile.DoesNotExist:
            raise serializers.ValidationError("Profile with this api_key does not exist.")
        
        # Attach the retrieved profile to the context for later use in views
        self.context['profile'] = profile
        return value

    def validate_bank(self, data):
        # Check if the bank exists as you did before
        bank_name = data.get('bank')
        if not Bank.objects.filter(bank_name=bank_name).exists():
            raise serializers.ValidationError("Bank doesn't exist.")
        
        return Bank.objects.get(bank_name=bank_name).id

class EventSerializer(ModelSerializer):
    # invitees = serializers.ListField(child=serializers.CharField(), required=False)  # Make invitees not required

    class Meta:
        model = Event
        fields = '__all__'

class ComplaintSerializer(ModelSerializer):
    
    class Meta:
        model = Complaint
        fields = "__all__"

    def validate_title(self, value):
        if value.strip() == "":
            raise ValidationError("Title cant be blank!")
        return value

    def validate_complaint(self, value):
        if value.strip() == "":
            raise ValidationError("Complaint can't be blank!")

        return value

    def validate_proposed_solution(self, value):
        if value.strip() == "":
            raise ValidationError("You must enter a proposed solution!")
        return value

class NewsSerializer(ModelSerializer):
    class Meta:
        model = News
        exclude = ["active", "verified"]


class GroupChatSerializer(ModelSerializer):
    department = DepartmentSerializer()
    class Meta:
        model = GroupChat
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["department"] = data["department"]["title"]
        members_array = []
        for member in data["members"]:
            user = Profile.objects.get(id = member)
            members_array.append(user.first_name + " " + user.last_name)
        data["members"] = members_array
        return data

class ChatMessageSerializer(ModelSerializer):
    class Meta:
        model = ChatMessage
        exclude = ["seen_by", "id"]

    def validate_message(self, value):
        if value.strip() == "":
            raise ValidationError("Message can't be empty!")
        return value

class ChatMessageSerializerGet(ModelSerializer):
    group = GroupChatSerializer()
    class Meta:
        model = ChatMessage
        exclude = ["seen_by", "id"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        data["group"] = data["group"]["title"]

        return data

class QuerySerializer(ModelSerializer):
    addressed_to = ProfileSerializer()
    class Meta:
        fields = "__all__"
        model = Query

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data["addressed_to"] = data["addressed_to"]["first_name"] + " " + data["addressed_to"]["last_name"]

        return data

class LogSerializer(ModelSerializer):
    user = ProfileSerializer()
    class Meta:
        model = Log
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data["user"] = data["user"]["first_name"] + " " + data["user"]["last_name"]

        return data

class NotificationSerializer(ModelSerializer):
    user = ProfileSerializer()
    class Meta:
        model = Notification
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data["user"] = data["user"]["first_name"] + " " + data["user"]["last_name"]

        return data
