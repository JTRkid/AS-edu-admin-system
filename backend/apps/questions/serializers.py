"""题目序列化器"""

from rest_framework import serializers
from .models import Question


class QuestionSerializer(serializers.ModelSerializer):
    """题目序列化器"""
    class Meta:
        model = Question
        fields = '__all__'
        read_only_fields = ['created_at']
