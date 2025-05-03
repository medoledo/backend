from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudyWeekViewSet, StudyMaterialViewSet

router = DefaultRouter()
router.register('weeks', StudyWeekViewSet, basename='studyweek')
router.register('materials', StudyMaterialViewSet, basename='studymaterial')

urlpatterns = [
    path('', include(router.urls)),
]
