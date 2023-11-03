import re
from rest_framework.serializers import ModelSerializer
from main.models import Profile
from rest_framework.validators import ValidationError

class ProfileSerializer(ModelSerializer):
    class Meta:
        model = Profile
        exclude = ["user","position", "department", "id_no", "salary", "is_premium_user", "api_token"]

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

class BankAccountView(ModelSerializer):
    class Meta:
        fields = "__all__"