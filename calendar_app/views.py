from rest_framework.viewsets import ViewSet
from .serializers import EventSerializer
from rest_framework.response import Response
from rest_framework import status
from .models import Event
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from drf_yasg.utils import swagger_auto_schema
import requests
from rest_framework.request import Request

from drf_yasg import openapi

class EventViewSet(ViewSet):

    serializer_class = EventSerializer
    pagination_class = LimitOffsetPagination

    def send_get_events_by_customer_to_odoo(self, customer_id):
        """
    Send GET request to Odoo to get all calendar events for a specific customer.
    """
        odoo_url = f"http://crm.codestra.co/api/website/view-activity?customer_id={customer_id}"

        headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer tu_token_de_autenticacion'
    }

        try:
            
            response = requests.get(odoo_url, headers=headers)

            
            response.raise_for_status()  

            
            response_data = response.json()

           
            odoo_events = response_data.get('data', [])
            if not odoo_events:
                print("No events found for this customer.")
                return None

            return odoo_events

        except requests.exceptions.HTTPError as errh:
            print(f"HTTP error occurred: {errh} - Status Code: {response.status_code}")
            return None
        except requests.exceptions.RequestException as err:
            print(f"Error connecting to Odoo: {err}")
            return None
        except ValueError:
            print(f"Invalid JSON response from Odoo: {response.text}")
        return None
    
    def send_get_event_by_id_to_odoo(self, customer_id):
        """
        Send GET request to Odoo to get a calendar event by id.
        """
   
        odoo_url = f"http://crm.codestra.co/api/website/view-activity?activity_id={customer_id}"
    
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer tu_token_de_autenticacion'  
    }

        try:
            
            response = requests.get(odoo_url, headers=headers)

            
            if response.status_code == 200:
                return response.json() 
            else:
             
                print(f"Error getting event from Odoo: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            
            print(f"Error connecting to Odoo: {e}")
            return None


    @swagger_auto_schema(
    operation_description="List all calendar events for a specific customer",
    operation_summary="List calendar events by customer ID",
    manual_parameters=[
        openapi.Parameter('customer_id', openapi.IN_QUERY, description="Client ID to list events for a specific client", type=openapi.TYPE_STRING)
    ],
    tags=["Calendar"]
)
    
    def list(self, request):
        paginator = self.pagination_class()

        
        customer_id = request.query_params.get('customer_id', None)

       
        if not customer_id:
            return Response({"error": "Customer ID is required."}, status=status.HTTP_400_BAD_REQUEST)

       
        odoo_events = self.send_get_events_by_customer_to_odoo(customer_id)

        if isinstance(odoo_events, dict):
            
            odoo_events = odoo_events.get('events', [])

        if not odoo_events:
        
            return Response({"message": "No events found for this customer."}, status=status.HTTP_404_NOT_FOUND)

        
        result_page = paginator.paginate_queryset(odoo_events, request)

        if result_page is not None:
            serializer = EventSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)

        
        return Response(EventSerializer(odoo_events, many=True).data)

    
    @swagger_auto_schema(
        operation_description="Retrieve a calendar event by specific ID of that event",
        operation_summary="Retrieve a calendar event by id",
        tags=["Calendar"],
    )
    def retrieve(self, request, pk=None):

     
        """
        Retrieve the calendar event by ID from Odoo and return it.
        """
        
        odoo_event = self.send_get_event_by_id_to_odoo(pk)

        
        if odoo_event:
            
            return Response(odoo_event, status=status.HTTP_200_OK)
        
        else:

            
            
            return Response({"error": "Event not found in Odoo."}, status=status.HTTP_404_NOT_FOUND)
     
    @swagger_auto_schema(
        operation_description="Create a calendar event",
        operation_summary="Create a calendar event",
        tags=["Calendar"],
        request_body=EventSerializer
    )
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        
        serializer = self.serializer_class(event, data=request.data)
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
        except Event.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
