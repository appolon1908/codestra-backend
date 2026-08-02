from django.conf import settings
from rest_framework.viewsets import ViewSet, ModelViewSet
from .models import HeaderTitle, CaseStudy, FAQs, ContactUs, Logo, TaxPayer
from .serializers import HeaderTitleSerializer, CaseStudySerializer, FaqSerializer, ContactUsSerializer, LogoSerializer, TaxPayerSerializer
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated, AllowAny
from notification.service import EmailService
from rest_framework_simplejwt.authentication import JWTAuthentication
import requests



from employee.models import Career, CareerApplication, Requirement, Question, Option, Answer
from rest_framework.decorators import action
from employee.serializers import (
        CareerSerializer, 
        CareerInputSerializer,
        AnswerSerializer,
        CreateEmployeeSerializer,
        CareerApplicationSerializer,
        CareerApplicationInputSerializer,
)

     


class CaseStudyViewSet(ViewSet):

    def get_queryset(self):
        return CaseStudy.objects.all()

    @swagger_auto_schema(
        operation_description="List all Case Study",
        operation_summary="List all Case Study",
        tags=["CaseStudy"],
    )
    def list(self, request):
        queryset = self.get_queryset()
        serializer = CaseStudySerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Case Study Form",
        operation_summary="Case Study Form",
        tags=["CaseStudy"],
        request_body=CaseStudySerializer
    )
    def create(self, request):
        serializer = CaseStudySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Get a single Case Study",
        operation_summary="Get a single Case Study",
        tags=["CaseStudy"],
    )
    def retrieve(self, request, pk=None):
        try:
            case_study = CaseStudy.objects.get(pk=pk)
        except CaseStudy.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = CaseStudySerializer(case_study)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Update Case Study",
        operation_summary="Update Case Study",
        tags=["CaseStudy"],
        request_body=CaseStudySerializer
    )
    def update(self, request, pk=None):
        try:
            case_study = CaseStudy.objects.get(pk=pk)
        except CaseStudy.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = CaseStudySerializer(case_study, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete Case Study",
        operation_summary="Delete Case Study",
        tags=["CaseStudy"],
    )
    def destroy(self, request, pk=None):
        try:
            case_study = CaseStudy.objects.get(pk=pk)
        except CaseStudy.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        case_study.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @swagger_auto_schema(
        operation_description="Get Hero header title for case-study page",
        operation_summary="Get Hero header title for case-study page",
        tags=["CaseStudy"],
    )
    @action(detail=False, methods=['get'], url_path="hero/header-title/get")
    def get_blog_header_title(self, request):
        header_title = HeaderTitle.objects.filter(page='case_study').order_by('-created_at').first()
        
        if not header_title:
            return Response({'message': 'No header title found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(HeaderTitleSerializer(header_title).data, status=status.HTTP_200_OK)
    

    @swagger_auto_schema(
        operation_description="Create Hero Header Title for Case Study page",
        operation_summary="Create Hero Header Title for Case Study page",
        tags=["CaseStudy"],
        request_body=HeaderTitleSerializer
    )
    @action(detail=False, methods=['post'], url_path="hero/header-title")
    def create_blog_header_title(self, request):
        serializer = HeaderTitleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(page='case_study')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FAQsViewSet(ViewSet):

    def get_queryset(self):
        return FAQs.objects.all()

    @swagger_auto_schema(
        operation_description="FAQs",
        operation_summary="FAQs",
        tags=["FAQs"],
    )
    def list(self, request):
        queryset = self.get_queryset()
        serializer = FaqSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="FAQs form",
        operation_summary="FAQs form",
        tags=["FAQs"],
    )
    def create(self, request):
        serializer = FaqSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Retrieve FAQs",
        operation_summary="Retrieve FAQs",
        tags=["FAQs"],
    )
    def retrieve(self, request, pk=None):
        try:
            faq = FAQs.objects.get(pk=pk)
        except FAQs.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = FaqSerializer(faq)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Update FAQs",
        operation_summary="Update FAQs",
        tags=["FAQs"],
    )
    def update(self, request, pk=None):
        try:
            faq = FAQs.objects.get(pk=pk)
        except FAQs.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = FaqSerializer(faq, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete FAQs",
        operation_summary="Delete FAQs",
        tags=["FAQs"],
    )
    def destroy(self, request, pk=None):
        try:
            faq = FAQs.objects.get(pk=pk)
        except FAQs.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        faq.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class ContactUsViewSet(ViewSet):
    
    def get_queryset(self):
        return super().get_queryset()
    
    @swagger_auto_schema(
        operation_description="Contact Us form",
        operation_summary="Contact Us form",
        tags=["contact-us"],
        request_body=ContactUsSerializer
    )
    def create(self, request):
        serializer = ContactUsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        contact = ContactUs.objects.create(
            **serializer.validated_data
        )
        
        # send email to our mail address
        EmailService.send_async(
            template="contact_us.html",
            subject="Contact Us Request",
            recipients=[settings.ADMIN_EMAIL],
            context={
                "full_name": serializer.validated_data.get('full_name'),
                "email": serializer.validated_data.get('email'),
                "company_size": serializer.validated_data.get('company_size'),
                "message": serializer.validated_data.get('message'),
            }
        )
        
        return Response({"message": "Thank you for contacting us"}, status=status.HTTP_201_CREATED)
    
    @swagger_auto_schema(
        operation_description="Contact Us",
        operation_summary="Contact Us",
        tags=["contact-us"],
    )
    def list(self, request):
        queryset = ContactUs.objects.all()
        serializer = ContactUsSerializer(queryset, many=True)
        return Response(serializer.data)
    
    

class LogoViewSet(ViewSet):
    def get_queryset(self):
        return Logo.objects.all().order_by('-created_at')
    
    
    @swagger_auto_schema(
        operation_description="Home page logo",
        operation_summary="Home page logo",
        tags=["home-page-logo"],
    )
    def list(self, request):
        queryset = self.get_queryset()
        serializer = LogoSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Home page logo form",
        operation_summary="Home page logo form",
        tags=["home-page-logo"],
        request_body=LogoSerializer
    )
    def create(self, request):
        serializer = LogoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Home page logo",
        operation_summary="Home page logo",
        tags=["home-page-logo"],
    )
    def retrieve(self, request, pk=None):
        try:
            logo = Logo.objects.get(pk=pk)
        except Logo.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = LogoSerializer(logo)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Home page logo",
        operation_summary="Home page logo",
        tags=["home-page-logo"],
    )
    def update(self, request, pk=None):
        try:
            logo = Logo.objects.get(pk=pk)
        except Logo.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = LogoSerializer(logo, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Home page logo",
        operation_summary="Home page logo",
        tags=["home-page-logo"],
    )
    def destroy(self, request, pk=None):
        try:
            logo = Logo.objects.get(pk=pk)
        except Logo.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        logo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class TaxPayerViewSet(ViewSet):

    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return TaxPayer.objects.all()

    @swagger_auto_schema(
        operation_description="List Taxpayers registration",
        operation_summary="List Taxpayers registration",
        tags=["tax-payer"],
    )
    def list(self, request):
        queryset = self.get_queryset()
        serializer = TaxPayerSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Taxpayer registration form",
        operation_summary="Taxpayer registration form",
        tags=["tax-payer"],
        request_body=TaxPayerSerializer
    )
    
    def create(self, request):
        # First, we create the TaxPayer object using the serializerer
        serializer = TaxPayerSerializer(data=request.data)
        
        if serializer.is_valid():
            
            try:
                #Ensure that the relationship between the user and the form is made
                serializer.validated_data['user'] = request.user 
                #  Save the form
                
                form = serializer.save()

                # Send the data to Odoo
                odoo_response = self.send_to_odoo(request,request.data)

                if odoo_response:
                    # If Odoo's response was successful, you can return it in the response
                    return Response({"form_data": serializer.data, "odoo_response": odoo_response}, status=status.HTTP_201_CREATED)
                else:
                    # If there was an error with the integration in Odoo, it returns an error
                    return Response({"error": "Error sending data to Odoo."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            except Exception as e:
                return Response({"error": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def send_to_odoo(self, request, data):
        """
        This function is responsible for sending the data to Odoo after the taxpayer is created.
        It receives the JSON directly from the request and processes it.
        """
        odoo_url = 'https://crm.codestra.co/contribuyente/register'  # 
        odoo_api_key = 'mi-api-key'  # Change this to your Odoo API Key if needed
    
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer tu_token_de_autenticacion'  # include a valid token if needed
        }
    
        #  Send data to Odoo in JSON format
        odoo_data = {
            "taxpayer_rnc": data.get("tax_payer_rnc"),
            "taxpayer_name": data.get("name_of_tax_payer"),
            "trade_name": data.get("trade_name"),
            "taxpayer_telephone": data.get("tax_payer_telephone"),
            "taxpayer_cell_phone": data.get("tax_payer_cell_phone"),
            "taxpayer_email": data.get("tax_payer_email"),
            "taxpayer_number": data.get("tax_payer_number"),
            "taxpayer_sector": data.get("tax_payer_sector"),
            "taxpayer_province": data.get("tax_payer_province"),
            "address_reference": data.get("address_reference"),
            "visiting_hours": data.get("visiting_hours"),
            "representation_rnc": data.get("representation_rnc"),
            "name_of_representative": data.get("name_of_representative"),
            "representative_phone": data.get("representative_phone"),
            "representative_cell_phone": data.get("representative_cell_phone"),
            "representative_email": data.get("representative_email"),
            "street_of_warehouse": data.get("street_of_warehouse"),
            "store_or_warehouse_number": data.get("store_or_warehouse_number"),
            "province_of_warehouse": data.get("province_of_warehouse"),
            "warehouse_reference": data.get("warehouse_reference"),
            "local_administration": data.get("local_administration"),
            "warehouse_sector": data.get("warehouse_sector"),
            "operation_carried_out_in_premise": data.get("operation_carried_out_in_premise"),
    
            # If the media file is present, use the URL
            "media_file": data.get("media_file") if data.get("media_file") else None,
            "odoo_id": request.user.odoo_id
        }
    
       
        try:
            response = requests.post(odoo_url, headers=headers, json=odoo_data)
            
            if response.status_code == 200:
              
                return response.json()
            else:
                
                print(f"Error in Odoo. Status Code: {response.status_code}, Mensaje: {response.text}")
                raise Exception(f"Error sending data to Odoo: {response.text}")
        
        except requests.exceptions.RequestException as e:
            
            print(f"Error sending data to Odoo: {str(e)}")
            raise Exception(f"Odoo connection error: {str(e)}")
     

    @swagger_auto_schema(
        operation_description="Retrieve Taxpayer",
        operation_summary="Retrieve Taxpayer",
        tags=["tax-payer"],
    )
    def retrieve(self, request, pk=None):
        try:
            taxpayer = TaxPayer.objects.get(pk=pk)
        except TaxPayer.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = TaxPayerSerializer(taxpayer)
        return Response(serializer.data)


    @swagger_auto_schema(
        operation_description="Update taxpayer registration form",
        operation_summary="Update taxpayer registration form",
        tags=["tax-payer"],
        request_body=TaxPayerSerializer
    )
    @action(detail=False, methods=['post'])
    def updateForm(self, request):
    
        serializer = TaxPayerSerializer( data=request.data, partial=True)
    
        if serializer.is_valid():

            serializer.validated_data['user'] = request.user
     
            
            updated_taxpayer = serializer.save()

         
            try:
                odoo_response = self.send_update_to_odoo(request, request.data)
                if odoo_response:
         
                    return Response({
                        "form_data": serializer.data, 
                        "odoo_response": odoo_response
                },      status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Error sending data to Odoo."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_update_to_odoo(self, request, data):
        
        """
        This feature sends the updated data to Odoo.
        """
        odoo_url = 'https://crm.codestra.co/contribuyente/register'  
        odoo_api_key = 'my-api-key'  

        headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {odoo_api_key}'
        }

        
        odoo_data = {
        "taxpayer_rnc": data.get("tax_payer_rnc"),
        "taxpayer_name": data.get("name_of_tax_payer"),
        "trade_name": data.get("trade_name"),
        "taxpayer_telephone": data.get("tax_payer_telephone"),
        "taxpayer_cell_phone": data.get("tax_payer_cell_phone"),
        "taxpayer_email": data.get("tax_payer_email"),
        "taxpayer_number": data.get("tax_payer_number"),
        "taxpayer_sector": data.get("tax_payer_sector"),
        "taxpayer_province": data.get("tax_payer_province"),
        "address_reference": data.get("address_reference"),
        "visiting_hours": data.get("visiting_hours"),
        "representation_rnc": data.get("representation_rnc"),
        "name_of_representative": data.get("name_of_representative"),
        "representative_phone": data.get("representative_phone"),
        "representative_cell_phone": data.get("representative_cell_phone"),
        "representative_email": data.get("representative_email"),
        "street_of_warehouse": data.get("street_of_warehouse"),
        "store_or_warehouse_number": data.get("store_or_warehouse_number"),
        "province_of_warehouse": data.get("province_of_warehouse"),
        "warehouse_reference": data.get("warehouse_reference"),
        "local_administration": data.get("local_administration"),
        "warehouse_sector": data.get("warehouse_sector"),
        "operation_carried_out_in_premise": data.get("operation_carried_out_in_premise"),

    
        "media_file": data.get("media_file") if data.get("media_file") else None,
        "odoo_id": request.user.odoo_id
    }

      
        try:
            response = requests.post(odoo_url, headers=headers, json=odoo_data)
        
            if response.status_code == 200:
              
                return response.json()
            else:
                print(f"Error in Odoo. Status Code: {response.status_code}, Mensaje: {response.text}")
                raise Exception(f"Error sending data to Odoo: {response.text}")
    
        except requests.exceptions.RequestException as e:
            print(f"Odoo request failed: {str(e)}")
            raise Exception(f"Odoo connection error: {str(e)}")


    @swagger_auto_schema(
        operation_description="Delete Taxpayer",
        operation_summary="Delete Taxpayer",
        tags=["tax-payer"],
        request_body=TaxPayerSerializer
    )
    def destroy(self, request, pk=None):
        try:
            taxpayer = TaxPayer.objects.get(pk=pk)
        except TaxPayer.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        taxpayer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

     
class CareerViewSet(ViewSet):
    queryset = Career.objects.all()
    serializer_class = CareerSerializer
    
    @swagger_auto_schema(
        operation_description="Candidate job application",
        operation_summary="Candidate job application",
        tags=["career"],
        request_body=CareerInputSerializer
    )
    def create(self, request):
        serializer = CareerInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        requirements = serializer.validated_data.pop("requirements")
        
        career = Career.objects.create(**serializer.validated_data)

        Requirement.objects.bulk_create([
            Requirement(career=career, description=req.get('description'))
            for req in requirements
        ])
        return Response({"message": "Career created successfully"}, status=status.HTTP_201_CREATED)
    
    @swagger_auto_schema(
        operation_description="Candidate job application",
        operation_summary="Candidate job application",
        tags=["career"]
    )
    def list(self, request):
        career = self.queryset
        return Response(CareerSerializer(career, many=True).data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_description="Candidate job application",
        operation_summary="Candidate job application",
        tags=["career"],
    )
    def retrieve(self, request, pk=None):
        career = Career.objects.filter(id=pk).first()
        return Response(
            CareerSerializer(career).data,
            status=status.HTTP_200_OK
        )
        
        
    @swagger_auto_schema(
        operation_description="Candidate job application",
        operation_summary="Candidate job application",
        tags=["career"],
    )
    @action(methods=["GET"], detail=True)
    def applications(self, request, pk=None):
        career = Career.objects.filter(id=pk)
        
        if not career.exists():
            return Response({'error': 'Career not found'}, status=status.HTTP_404_NOT_FOUND)
        
        applications = CareerApplication.objects.filter(
            career=career.first()
        )
        return Response(CareerApplicationSerializer(applications).data, status=status.HTTP_200_OK)
    
    
    @swagger_auto_schema(
        operation_description="Candidate job application",
        operation_summary="Candidate job application",
        tags=["career"],
        request_body=CareerApplicationInputSerializer
    )
    @action(methods=['POST'], detail=False, url_path="application")
    def create_application(self, request):
        serializer = CareerApplicationInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        career = Career.objects.filter(id=serializer.validated_data.get("career_id"))
        
        if not career.exists():
            return Response({'error': 'Career not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            career_application = CareerApplication.objects.create(
                career=career.first(),
                **serializer.validated_data
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(CareerApplicationSerializer(career_application).data, status=status.HTTP_201_CREATED)
        
    
    @swagger_auto_schema(
        operation_description="List Candidate job applications",
        operation_summary="List Candidate job applications",
        tags=["career"]
    )
    @action(methods=['GET'], detail=False, url_path="applications")
    def list_applications(self, request):
        
        career_application = CareerApplication.objects.all()
        
        return Response(CareerApplicationSerializer(career_application, many=True).data, status=status.HTTP_201_CREATED)
        
    @swagger_auto_schema(
        operation_description="Retrieve Candidate job applications",
        operation_summary="Retrieve Candidate job applications",
        tags=["career"]
    )
    @action(methods=['GET'], detail=False, url_path="applications/(?P<pk>[a-z,A-Z,0-9]+)")
    def retrieve_application(self, request, pk=None):
        
        career_application = CareerApplication.objects.filter(id=pk).first()
        
        return Response(CareerApplicationSerializer(career_application).data, status=status.HTTP_201_CREATED)
        
    
    

class AnswerViewSet(ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)