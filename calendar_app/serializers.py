from rest_framework import serializers
from .models import Event
from employee.models import Employee
from employee.serializers import EmployeeSerializer



class EventSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = "__all__"
        