from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ScoreViewSet, score_submit_api

router = DefaultRouter()
router.register(r'', ScoreViewSet, basename='score')

urlpatterns = [
    path('submit/', score_submit_api, name='score_submit'),
    path('', include(router.urls)),
]
