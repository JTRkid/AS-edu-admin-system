"""答案提交管理视图 — 提交CRUD、截止时间/重复提交控制"""

from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Submission
from apps.questions.models import Question
from .serializers import SubmissionSerializer, SubmissionCreateSerializer


class SubmissionViewSet(viewsets.ModelViewSet):
    """答案提交ViewSet，学生只能查看自己的提交，支持重新提交（覆盖旧答案）"""
    queryset = Submission.objects.select_related('student', 'question').all()
    filterset_fields = ['section', 'question', 'student']

    def get_serializer_class(self):
        if self.action == 'create':
            return SubmissionCreateSerializer
        return SubmissionSerializer

    # FIXME: perform_create 的截止时间和重复提交检查永远不会执行，
    # 因为 create() 方法已覆盖了全部逻辑，perform_create 仅在 create 末尾被调用一次
    def perform_create(self, serializer):
        # Check deadline
        question = serializer.validated_data.get('question')
        if question.deadline and timezone.now() > question.deadline:
            return Response({'code': 400, 'message': '已超过答题截止时间'}, status=400)

        # Check if allow resubmit
        if not question.allow_resubmit:
            existing = Submission.objects.filter(
                student=self.request.user, question=question
            ).exists()
            if existing:
                return Response({'code': 400, 'message': '该题目不允许重复提交'}, status=400)

        serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question = serializer.validated_data.get('question')
        if question.deadline and timezone.now() > question.deadline:
            return Response({'code': 400, 'message': '已超过答题截止时间'}, status=400)

        existing = Submission.objects.filter(student=request.user, question=question).first()
        if existing:
            if not question.allow_resubmit:
                return Response({'code': 400, 'message': '该题目不允许重复提交'}, status=400)
            # Overwrite existing submission
            existing.answer = serializer.validated_data.get('answer', '')
            existing.language = serializer.validated_data.get('language', '')
            existing.section = serializer.validated_data.get('section', existing.section)
            existing.save()
            return Response({
                'code': 200,
                'message': '重新提交成功',
                'data': SubmissionSerializer(existing).data,
            }, status=200)

        self.perform_create(serializer)
        return Response({
            'code': 200,
            'message': '提交成功',
            'data': SubmissionSerializer(serializer.instance).data,
        }, status=201)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # Students can only see their own submissions
        if request.user.role == 'student':
            queryset = queryset.filter(student=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubmissionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = SubmissionSerializer(queryset, many=True)
        return Response({'code': 200, 'data': serializer.data})

    @action(methods=['get'], detail=False)
    def my(self, request):
        """学生查看自己的提交"""
        queryset = Submission.objects.filter(student=request.user)
        section_id = request.query_params.get('section_id')
        if section_id:
            queryset = queryset.filter(section_id=section_id)
        serializer = SubmissionSerializer(queryset, many=True)
        return Response({'code': 200, 'data': serializer.data})
