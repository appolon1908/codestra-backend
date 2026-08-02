from django.urls import path
from rest_framework.routers import DefaultRouter

from blog_app.views import BlogViewSet

router = DefaultRouter()


router.register('', BlogViewSet, basename='blog')

urlpatterns = router.urls