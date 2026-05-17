from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, ChapterViewSet, SectionViewSet

course_router = DefaultRouter()
course_router.register(r'', CourseViewSet, basename='course')

chapter_router = DefaultRouter()
chapter_router.register(r'', ChapterViewSet, basename='chapter')

section_router = DefaultRouter()
section_router.register(r'', SectionViewSet, basename='section')

urlpatterns = [
    path('chapters/', include(chapter_router.urls)),
    path('sections/', include(section_router.urls)),
    path('', include(course_router.urls)),
]
