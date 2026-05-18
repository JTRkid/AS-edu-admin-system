"""答案提交序列化器"""

from rest_framework import serializers
from .models import Submission


class SubmissionSerializer(serializers.ModelSerializer):
    """提交记录序列化器，包含学生姓名和学号"""
    student_name = serializers.CharField(source='student.name', read_only=True)
    # TODO: get_student_no 对每条序列化记录执行一次 DB 查询，存在 N+1 问题
    student_no = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = '__all__'
        read_only_fields = ['student', 'submitted_at']

    def get_student_no(self, obj):
        from apps.accounts.models import Student
        try:
            return Student.objects.get(user=obj.student).student_no
        except Student.DoesNotExist:
            return ''


class SubmissionCreateSerializer(serializers.ModelSerializer):
    """创建提交的序列化器，自动注入当前用户和客户端IP"""
    class Meta:
        model = Submission
        fields = ['question', 'section', 'answer', 'language']

    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        validated_data['ip_address'] = self.get_client_ip(self.context['request'])
        return super().create(validated_data)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR', '')
