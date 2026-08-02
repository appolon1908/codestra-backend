from rest_framework import status, serializers
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
import requests
from django.contrib.auth.hashers import check_password
import logging
from .models import User, Visitor
from .serializers import UserSerializer, VisitorSerializer, GetUserSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth import authenticate, login
import base64

logger = logging.getLogger(__name__)


class AuthViewSet(ViewSet):
    
    @swagger_auto_schema(
        operation_description="Sign up user",
        operation_summary="Sign up user",
        tags=["Auth"],
        request_body=UserSerializer
    )
    @action(detail=False, methods=['POST'])
   
    def signup(self, request):
        serializer = UserSerializer(data=request.data)
    
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            logger.error(f"Validation error: {e.detail}")
            return Response({'errors': e.detail}, status=status.HTTP_400_BAD_REQUEST)

        profile_picture_base64 = None
        if 'profile_picture' in request.FILES:
            with open(request.FILES['profile_picture'].name, 'rb') as img_file:
                profile_picture_base64 = base64.b64encode(img_file.read()).decode('utf-8')

        
       
        odoo_data = {
            'first_name': f"{request.data['first_name']}", 
            'last_name': f"{request.data['last_name']}",
            'email': request.data['email'],
            'phone': request.data.get('phone_number'),
            'plan_type': request.data.get('plan_type', 'FREE'), 
            'profile_picture': profile_picture_base64 
    }

        odoo_api_url = "https://crm.codestra.co/api/website/register"  
        odoo_response = requests.post(odoo_api_url, json=odoo_data)

        if odoo_response.status_code == 200:
            try:
                odoo_response_data = odoo_response.json()
                odoo_client_id = odoo_response_data.get("result", {}).get('id')

                if odoo_client_id:
                    
                    user = User.objects.create_user(
                    email=serializer.validated_data['email'],
                    first_name=serializer.validated_data['first_name'],
                    last_name=serializer.validated_data['last_name'],
                    phone_number=serializer.validated_data.get('phone_number'),
                    password=serializer.validated_data['password'],
                    timezone=serializer.validated_data.get('timezone'),
                    odoo_id=odoo_client_id,  
                )

                   
                    profile_picture = request.FILES.get('profile_picture')
                   
                    if profile_picture:
                        user.profile_picture.save(profile_picture.name, profile_picture)

                    return Response({
                        "message": "Sign up successful",
                        "odoo_client_id": odoo_client_id
                },      status=status.HTTP_201_CREATED)

                else:
                    return Response({
                    "message": "Error: No Odoo ID returned",
                    "error": "Odoo API did not return a valid client ID"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            except ValueError as e:
                return Response({
                    "message": "Error processing Odoo response",
                    "error": str(e)
            },      status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
        else:
            return Response({
                "message": "Error communicating with Odoo",
                "error": f"Odoo API returned status code {odoo_response.status_code}"
        },      status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(
            operation_description="log in user",
            operation_summary="log in user",
            tags=["Auth"],
            request_body=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address'),
                        'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
                    },
                    required=['email', 'password']
                )
        )
    @action(detail=False, methods=['POST'])
    def login_view(self, request):
            email = request.data.get('email')
            password = request.data.get('password')

            user = User.objects.filter(email=email).first()
            if not user:
                return Response({'message': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

            user_password = check_password(password, user.password)
            if not user_password:
                return Response(errors={"error": "incorrect email/password"}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken.for_user(user)
            data = {
                "user": GetUserSerializer(instance=user).data,
                "token": {"refresh": str(token), "access": str(token.access_token)},
            }

            return Response(data, status=status.HTTP_200_OK)
    
    
    @swagger_auto_schema(
        operation_description="Log Out user",
        operation_summary="Log Out user",
        tags=["Auth"],
        request_body=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='refresh_token'),
                },
                required=['refresh']
            )
    )
    @action(detail=False, methods=['POST'])
    def logout(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
    @swagger_auto_schema(
    method='get',
    operation_description="Checks if the user is authenticated and displays the sessionid if it is.",
    operation_summary="User session verification",
    tags=["Auth"],
    responses={
            200: openapi.Response("Authenticated user", examples={
                "application/json": {
                    "message": "User is authenticated",
                    "sessionid": "example-session-id"
                }
            }),
            401: openapi.Response("Unauthenticated user", examples={
                "application/json": {
                    "message": "User is not authenticated"
                }
            })
        }
    )
    @action(detail=False, methods=['get'])
    def check_session(self, request):
        """
        It checks if the user is authenticated and displays the sessionid if they are.
        """
       
        if request.user.is_authenticated:
          
            return Response({
                "message": "User is authenticated",
                "user": {
                    'id': request.user.id,
                    'email': request.user.email,
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name
                }
            })
        else:
            return Response({"message": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

class UserViewSet(ViewSet):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    
    @swagger_auto_schema(
        operation_description="List Users",
        operation_summary="List Users",
        tags=["Auth"],
    )
    def list(self, request):
        users = User.objects.all()
        return Response(UserSerializer(users, many=True).data)
    
    @swagger_auto_schema(
        operation_description="Retrieve User",
        operation_summary="Retrieve User",
        tags=["Auth"],
    )
    def retrieve(self, request, pk=None):
        user = User.objects.filter(id=pk).first()
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="User details",
        operation_summary="User details",
        tags=["Auth"],
    )
    @action(detail=False, methods=['get'])
    def me(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)
    

    @swagger_auto_schema(
        operation_description="Update user",
        operation_summary="Update user",
        tags=["Auth"],
        request_body=UserSerializer
    )
    def update(self, request, pk=None):
        user = User.objects.filter(id=pk).first()
        serializer = UserSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        user.email = serializer.validated_data.get('email', user.email)
        user.first_name = serializer.validated_data.get('first_name', user.first_name)
        user.last_name = serializer.validated_data.get('last_name', user.last_name)
        user.phone_number = serializer.validated_data.get('phone_number', user.phone_number)

        user.is_active = serializer.validated_data.get('is_active', user.is_active)
        user.is_staff = serializer.validated_data.get('is_staff', user.is_staff)
        user.is_superuser = serializer.validated_data.get('is_superuser', user.is_superuser)
        user.save()
        return Response(UserSerializer(user).data)
    
    @swagger_auto_schema(
        operation_description="Delete User",
        operation_summary="Delete User",
        tags=["Auth"],
    )
    def destroy(self, request, pk=None):
        user = User.objects.filter(id=pk).first()
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)