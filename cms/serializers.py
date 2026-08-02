from rest_framework import serializers
from .models import HeaderTitle, CaseStudy, FAQs, ContactUs, Logo, TaxPayer
from auth_app.models import User


class HeaderTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeaderTitle
        fields = "__all__"
        

class CaseStudySerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseStudy
        fields = "__all__"
        

class LogoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logo
        fields = "__all__"

class FaqSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQs
        fields = "__all__"
        

class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = "__all__"



class TaxPayerSerializer(serializers.ModelSerializer):

    user = serializers.PrimaryKeyRelatedField(required=False, read_only=True)

    class Meta:
        model = TaxPayer
        fields = "__all__"
        

    