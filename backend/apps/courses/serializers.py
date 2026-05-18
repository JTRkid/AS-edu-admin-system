"""课程序列化器 — Course/Chapter/Section 及简化版序列化器"""

from rest_framework import serializers
from .models import Course, Chapter, Section


class SectionSerializer(serializers.ModelSerializer):
    """节序列化器，包含所属章号"""
    chapter_no = serializers.IntegerField(source='chapter.chapter_no', read_only=True)
    chapter_title = serializers.CharField(source='chapter.title', read_only=True)

    class Meta:
        model = Section
        fields = '__all__'
        read_only_fields = ['created_at']


class ChapterSerializer(serializers.ModelSerializer):
    """章序列化器，嵌套包含下属节列表"""
    sections = SectionSerializer(many=True, read_only=True)

    class Meta:
        model = Chapter
        fields = '__all__'
        read_only_fields = ['created_at']


class ChapterSimpleSerializer(serializers.ModelSerializer):
    """章简化序列化器（不含嵌套节）"""
    class Meta:
        model = Chapter
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    """课程序列化器，嵌套包含章-节树结构"""
    chapters = ChapterSerializer(many=True, read_only=True)
    teacher_name = serializers.CharField(source='teacher.name', read_only=True)

    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ['teacher', 'created_at']


class CourseSimpleSerializer(serializers.ModelSerializer):
    """课程简化序列化器（仅 id/name/status）"""
    class Meta:
        model = Course
        fields = ['id', 'name', 'status']
