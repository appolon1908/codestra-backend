from rest_framework import serializers
from .models import User, Visitor



class UserSerializer(serializers.ModelSerializer):
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Invalid credentials, please try another value.')
        return value
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone_number', 'client_id', 'created_at', 'updated_at', 'profile_picture', 'timezone', 'plan_type', 'trial_expiry_date', 'password']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {'password': {'write_only': True}}
        
class GetUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone_number', 'created_at', 'updated_at', 'profile_picture', 'timezone', 'plan_type', 'trial_expiry_date']
        read_only_fields = ['id', 'created_at', 'updated_at']
        

class GetShortUserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'profile_picture']
        read_only_fields = ['id']
        
        
class VisitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visitor
        fields = ['id', 'ip_address', 'blog', 'created_at']
        read_only_fields = ['id', 'created_at']