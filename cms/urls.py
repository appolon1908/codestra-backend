from .views import (
        LogoViewSet,
        FAQsViewSet, 
        ContactUsViewSet,
        CaseStudyViewSet, 
        TaxPayerViewSet,
        AnswerViewSet,
        CareerViewSet,
        )

from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()


router.register(r'case-study', CaseStudyViewSet, basename='case-study')
router.register(r'faqs', FAQsViewSet, basename='faq')
router.register(r'contact-us', ContactUsViewSet, basename='contact-us')
router.register(r'logo', LogoViewSet, basename='logo')
router.register(r'tax-payer', TaxPayerViewSet, basename='tax-payer')
router.register(r'careers', CareerViewSet, basename="careers")
router.register(r'answers', AnswerViewSet, basename="answers")

urlpatterns = [
    path('', include(router.urls)),
]