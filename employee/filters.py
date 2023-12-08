import django_filters
from main.models import Profile
from django.db import models

class ProfileFilter(django_filters.FilterSet):
    class Meta:
        model = Profile
        fields = {
            'title': ['exact', 'icontains'],
            'salary': ['exact', 'icontains'],
            'nationality': ['exact', 'icontains'],
            'position': ['exact'],
            'department': ['exact'],
        }
