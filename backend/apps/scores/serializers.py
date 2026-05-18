"""成绩序列化器 — Score序列化、ScoreSubmit(评分机提交)、Excel导入"""

from rest_framework import serializers
from .models import Score, ScoreHistory


class ScoreHistorySerializer(serializers.ModelSerializer):
    """成绩修改历史序列化器"""
    modified_by_name = serializers.CharField(source='modified_by.name', read_only=True)

    class Meta:
        model = ScoreHistory
        fields = '__all__'


class ScoreSerializer(serializers.ModelSerializer):
    """成绩序列化器，包含修改历史"""
    history = ScoreHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Score
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class ScoreSubmitSerializer(serializers.Serializer):
    """评分机提交成绩的序列化器，course_name 用于多课程场景下精确定位节"""
    student_no = serializers.CharField(max_length=20)
    class_name = serializers.CharField(max_length=50)
    student_name = serializers.CharField(max_length=50)
    chapter_no = serializers.IntegerField()
    section_no = serializers.IntegerField()
    course_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    chapter_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    section_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    score = serializers.DecimalField(max_digits=6, decimal_places=2)
    evaluator = serializers.CharField(max_length=100, required=False, allow_blank=True)
    details = serializers.CharField(required=False, allow_blank=True)
    timestamp = serializers.DateTimeField(required=False)


class ScoreImportSerializer(serializers.Serializer):
    """Excel导入成绩序列化器"""
    file = serializers.FileField()
