from rest_framework.viewsets import ViewSet
from .serializers import EventSerializer, CreateEventSerializer
from rest_framework.response import Response
from rest_framework import status
from .models import Event
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination

from drf_yasg.utils import swagger_auto_schema

from notification.service import EmailService
from employee.models import Employee



class EventViewSet(ViewSet):
    serializezr_class = EventSerializer
    pagination_class = LimitOffsetPagination
    
    @swagger_auto_schema(
        operation_description="List all calendar events",
        operation_summary="List all calendar events",
        tags=["Calendar"],
    )
    def list(self, request):
        paginator = self.pagination_class()
        events = Event.objects.all()

        result_page = paginator.paginate_queryset(events, request)

        if result_page is not None:
            serializer = EventSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        return Response(EventSerializer(blogs, many=True).data)
    

    @swagger_auto_schema(
        operation_description="Create a calendar event",
        operation_summary="Create a calendar event",
        tags=["Calendar"],
        request_body=EventSerializer
    )
    def create(self, request):
        serializer = CreateEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        employee = None
        
        if serializer.validated_data.get("employee_id"):
            employee = Employee.objects.filter(pk=serializer.validated_data['employee_id']).first()
            
            if not employee:
                return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if Event.objects.filter(
            employee=employee, 
            start_time=serializer.validated_data['start_time'], 
            end_time=serializer.validated_data['end_time']).exists():
            return Response({"error": "An event with the same start and end time already exists for this employee"}, status=status.HTTP_400_BAD_REQUEST)
        
        event = Event.objects.create(
            title=serializer.validated_data['title'],
            description=serializer.validated_data['description'],
            start_time=serializer.validated_data['start_time'],
            end_time=serializer.validated_data['end_time'],
            employee=employee,
            event_type=serializer.validated_data.get("event_type", "meeting"),
            created_by=request.user
        )
        
        # send event creation email
        subject = f"Event '{event.title}' created"
        recipient_list = [request.user.email, employee.email] if employee else [request.user.email]
        EmailService.send_async(
            template="event_creation_mail.html",
            subject=subject,
            recipients=recipient_list,
            context={
                "username": request.user.first_name,
                "event_name": event.title,
                "event_date": event.start_time
            }
        )
        
        # send email to admin
        EmailService.send_async(
            template="event_creation_admin_mail.html",
            subject=subject,
            recipients=[settings.ADMIN_EMAIL],
            context={
                "username": request.user.first_name,
                "event_name": event.title,
                "event_date": event.start_time
            })
        
        return Response(EventSerializer(event).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="Retrieve a calendar event",
        operation_summary="Retrieve a calendar event",
        tags=["Calendar"],
    )
    def retrieve(self, request, pk=None):
        try:
            event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializezr_class(event)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Update a calendar event",
        operation_summary="Update a calendar event",
        tags=["Calendar"],
        request_body=EventSerializer
    )
    def update(self, request, pk=None):
        try:
            event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializezr_class(event, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete a calendar event",
        operation_summary="Delete a calendar event",
        tags=["Calendar"],
    )
    def destroy(self, request, pk=None):
        try:
            event = Event.objects.get(pk=pk)
            # send email to admin
            subject = f"Event '{event.title}' deleted"
            EmailService.send_async(
                template="event_deletion_admin_mail.html",
                subject=subject,
                recipients=[settings.ADMIN_EMAIL],
                context={
                    "username": request.user.first_name,
                    "event_name": event.title,
                    "event_date": event.start_time
                })
        except Event.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)