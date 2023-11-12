import re
from rest_framework.serializers import ModelSerializer
from main.models import Profile, BankAccount, Bank, Complaint
from rest_framework.validators import ValidationError
from rest_framework import serializers
from admins.models import Event
class ProfileSerializer(ModelSerializer):
    class Meta:
        model = Profile
        # exclude = ["user","position", "department", "id_no", "salary", "is_premium_user"]
        fields = "__all__"
        read_only_fields = ("user","position", "department", "id_no", "salary", "is_premium_user")

    def validate_phone_number(self, value):
        if not re.match(r'^\+?[0-9]+$', value):
            raise ValidationError("Invalid phone number format.")

        return value

    def validate_title(self, value):
        if value  not in ["Dr", "Engr", "Miss", "Mr", "Mrs", "Prof"]:
            raise ValidationError("Invalid title")

        return value

    def validate_nationality(self, value):
        if not re.match(r'^[A-Za-z]+$', value):
            raise ValidationError("Invalid nationality")
        return value

    def validate_first_name(self, value):
        if not re.match(r'^[A-Za-z]+$', value):
            raise ValidationError("Name can only be texts")
        return value

    def validate_middle_name(self, value):
        if not re.match(r'^[A-Za-z]+$', value):
            raise ValidationError("Name can only be texts")
        return value

    def validate_last_name(self, value):
        if not re.match(r'^[A-Za-z]+$', value):
            raise ValidationError("Name can only be texts")
        return value

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
