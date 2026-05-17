from rest_framework import serializers
from .models import Course, Chapter, Section


class SectionSerializer(serializers.ModelSerializer):
    chapter_no = serializers.IntegerField(source='chapter.chapter_no', read_only=True)
    chapter_title = serializers.CharField(source='chapter.title', read_only=True)

    class Meta:
        model = Section
        fields = '__all__'
        read_only_fields = ['created_at']


class ChapterSerializer(serializers.ModelSerializer):
    sections = SectionSerializer(many=True, read_only=True)

    class Meta:
        model = Chapter
        fields = '__all__'
        read_only_fields = ['created_at']


class ChapterSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    chapters = ChapterSerializer(many=True, read_only=True)
    teacher_name = serializers.CharField(source='teacher.name', read_only=True)

    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ['teacher', 'created_at']


class CourseSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'status']
