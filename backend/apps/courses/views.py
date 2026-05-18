"""课程管理视图 — 课程/章/节CRUD、树结构、激活节切换"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Course, Chapter, Section
from .serializers import (
    CourseSerializer, CourseSimpleSerializer, ChapterSerializer,
    ChapterSimpleSerializer, SectionSerializer,
)


class CourseViewSet(viewsets.ModelViewSet):
    """课程ViewSet，自动关联当前教师为授课教师"""
    queryset = Course.objects.prefetch_related('chapters__sections').all()
    serializer_class = CourseSerializer
    filterset_fields = ['status']
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({'code': 200, 'data': serializer.data})

    @action(methods=['get'], detail=False)
    def simple(self, request):
        """返回课程简单列表（用于下拉选择）"""
        courses = Course.objects.filter(status='active')
        serializer = CourseSimpleSerializer(courses, many=True)
        return Response({'code': 200, 'data': serializer.data})

    @action(methods=['get'], detail=True)
    def tree(self, request, pk=None):
        """获取课程完整的章-节树结构"""
        course = self.get_object()
        serializer = CourseSerializer(course)
        return Response({'code': 200, 'data': serializer.data})


class ChapterViewSet(viewsets.ModelViewSet):
    """章ViewSet，支持按课程和可见性筛选"""
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer
    filterset_fields = ['course', 'is_visible']
    ordering_fields = ['sequence', 'chapter_no']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = ChapterSimpleSerializer(queryset, many=True)
        return Response({'code': 200, 'data': serializer.data})


class SectionViewSet(viewsets.ModelViewSet):
    """节ViewSet，支持激活节切换和当前激活节查询"""
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    filterset_fields = ['chapter', 'is_active', 'is_visible']
    ordering_fields = ['sequence', 'section_no']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({'code': 200, 'data': serializer.data})

    @action(methods=['post'], detail=True)
    def set_active(self, request, pk=None):
        """设置为当前激活的节"""
        section = self.get_object()
        # Deactivate all sections in the same chapter's course
        course = section.chapter.course
        Section.objects.filter(chapter__course=course).update(is_active=False)
        section.is_active = True
        section.save()
        return Response({'code': 200, 'message': '已设为当前节'})

    @action(methods=['get'], detail=False)
    def active(self, request):
        """获取当前激活的节"""
        course_id = request.query_params.get('course_id')
        qs = Section.objects.filter(is_active=True, is_visible=True)
        if course_id:
            qs = qs.filter(chapter__course_id=course_id)
        section = qs.first()
        if section:
            serializer = SectionSerializer(section)
            return Response({'code': 200, 'data': serializer.data})
        return Response({'code': 404, 'message': '无激活的节'}, status=404)
