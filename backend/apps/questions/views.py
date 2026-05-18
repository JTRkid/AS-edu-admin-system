"""题目管理视图 — 题目CRUD、发布/撤回、教师批改、成绩汇总"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import models as db_models
from django.db.models import Sum
from django.utils.dateparse import parse_datetime
from .models import Question
from .serializers import QuestionSerializer
from apps.submissions.models import Submission
from apps.submissions.serializers import SubmissionSerializer
from apps.scores.models import Score
from apps.accounts.models import Student
from apps.courses.models import Section


class QuestionViewSet(viewsets.ModelViewSet):
    """题目管理ViewSet，支持批量操作（发布/撤回/截止/删除）、教师批改和成绩生成"""
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    filterset_fields = ['section', 'type', 'is_published']
    ordering_fields = ['order_num', 'created_at']

    def perform_create(self, serializer):
        """自动分配 order_num 为当前节已有题目数+1"""
        section_id = serializer.validated_data.get('section').id if serializer.validated_data.get('section') else None
        if section_id:
            max_order = Question.objects.filter(section_id=section_id).aggregate(
                m=db_models.Max('order_num')
            )['m'] or 0
            serializer.save(order_num=max_order + 1)
        else:
            serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({'code': 200, 'message': '题目已添加', 'data': serializer.data}, status=201)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({'code': 200, 'message': '题目已更新', 'data': serializer.data})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'code': 200, 'message': '题目已删除'})

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({'code': 200, 'data': serializer.data})

    @action(methods=['post'], detail=True)
    def publish(self, request, pk=None):
        question = self.get_object()
        question.is_published = True
        question.save()
        return Response({'code': 200, 'message': '题目已发布'})

    @action(methods=['post'], detail=True)
    def unpublish(self, request, pk=None):
        question = self.get_object()
        question.is_published = False
        question.save()
        return Response({'code': 200, 'message': '题目已撤回'})

    @action(methods=['get'], detail=True)
    def submissions(self, request, pk=None):
        """获取某题目的所有学生提交（教师端批改用）"""
        question = self.get_object()
        subs = Submission.objects.filter(question=question).select_related('student')
        data = []
        for sub in subs:
            item = SubmissionSerializer(sub).data
            data.append(item)
        return Response({'code': 200, 'data': data})

    @action(methods=['post'], detail=True)
    def grade(self, request, pk=None):
        """教师批改题目并提交成绩"""
        question = self.get_object()
        submissions_data = request.data.get('submissions', [])

        if not submissions_data:
            return Response({'code': 400, 'message': '请提供批改数据'}, status=400)

        graded_count = 0
        for item in submissions_data:
            submission_id = item.get('submission_id')
            manual_score = item.get('score')  # 仅简答题需要手动给分

            try:
                sub = Submission.objects.get(id=submission_id, question=question)
            except Submission.DoesNotExist:
                continue

            # 自动批改：单选/多选/判断
            if question.type in ('single', 'multiple', 'judgment'):
                correct = question.correct_answer.strip()
                student_answer = sub.answer.strip()
                score = question.max_score if student_answer == correct else 0
            else:
                # 简答题：使用教师手动给的分数
                if manual_score is None:
                    continue
                score = manual_score

            # 创建或更新成绩记录
            try:
                student_profile = Student.objects.get(user=sub.student)
            except Student.DoesNotExist:
                continue

            score_record, _ = Score.objects.update_or_create(
                student=sub.student,
                section=question.section,
                score_type='regular',
                defaults={
                    'student_no': student_profile.student_no,
                    'student_name': sub.student.name,
                    'class_name': student_profile.class_name,
                    'chapter_no': question.section.chapter.chapter_no,
                    'chapter_name': question.section.chapter.title,
                    'section_no': question.section.section_no,
                    'section_name': question.section.title,
                    'score': score,
                    'score_type': 'regular',
                    'source': 'auto_script',
                    'evaluator': f'教师批改:{request.user.name}',
                    'details': f'题目:{question.title} 答案:{sub.answer}',
                }
            )
            graded_count += 1

        return Response({
            'code': 200,
            'message': f'批改完成，共处理{graded_count}条成绩',
            'data': {'graded_count': graded_count},
        })

    @action(methods=['get'], detail=False)
    def section_submissions(self, request):
        """获取某节下所有题目的提交（教师端批改用）"""
        section_id = request.query_params.get('section')
        if not section_id:
            return Response({'code': 400, 'message': '请提供节ID'}, status=400)

        questions = Question.objects.filter(section_id=section_id, is_published=True)
        result = []
        for q in questions:
            subs = Submission.objects.filter(question=q).select_related('student')
            q_data = QuestionSerializer(q).data
            q_data['submissions'] = SubmissionSerializer(subs, many=True).data
            result.append(q_data)

        return Response({'code': 200, 'data': result})

    @action(methods=['post'], detail=False)
    def batch_publish(self, request):
        """批量发布题目"""
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'code': 400, 'message': '请提供题目ID列表'}, status=400)
        Question.objects.filter(id__in=ids).update(is_published=True)
        return Response({'code': 200, 'message': f'已发布{len(ids)}道题目'})

    @action(methods=['post'], detail=False)
    def batch_unpublish(self, request):
        """批量撤回题目"""
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'code': 400, 'message': '请提供题目ID列表'}, status=400)
        Question.objects.filter(id__in=ids).update(is_published=False)
        return Response({'code': 200, 'message': f'已撤回{len(ids)}道题目'})

    @action(methods=['post'], detail=False)
    def batch_deadline(self, request):
        """批量设置截止时间"""
        ids = request.data.get('ids', [])
        deadline = request.data.get('deadline')
        if not ids:
            return Response({'code': 400, 'message': '请提供题目ID列表'}, status=400)
        dt = parse_datetime(deadline) if deadline else None
        Question.objects.filter(id__in=ids).update(deadline=dt)
        return Response({'code': 200, 'message': f'已为{len(ids)}道题目设置截止时间'})

    @action(methods=['post'], detail=False)
    def batch_delete(self, request):
        """批量删除题目"""
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'code': 400, 'message': '请提供题目ID列表'}, status=400)
        Question.objects.filter(id__in=ids).delete()
        return Response({'code': 200, 'message': f'已删除{len(ids)}道题目'})

    @action(methods=['get'], detail=False)
    def section_total(self, request):
        """获取节的题目总分"""
        section_id = request.query_params.get('section')
        if not section_id:
            return Response({'code': 400, 'message': '请提供节ID'}, status=400)
        total = Question.objects.filter(section_id=section_id).aggregate(
            s=Sum('max_score')
        )['s'] or 0
        return Response({'code': 200, 'data': {'total': float(total)}})

    @action(methods=['post'], detail=False)
    def section_grade(self, request):
        """提交某节所有学生的总成绩（按学号汇总）"""
        section_id = request.data.get('section_id')
        grades = request.data.get('grades', [])

        if not section_id or not grades:
            return Response({'code': 400, 'message': '请提供节ID和成绩数据'}, status=400)

        try:
            section = Section.objects.get(id=section_id)
        except Section.DoesNotExist:
            return Response({'code': 404, 'message': '节不存在'}, status=404)

        graded_count = 0
        for item in grades:
            student_id = item.get('student_id')
            total_score = item.get('total_score', 0)
            details = item.get('details', '')

            try:
                student_profile = Student.objects.get(user_id=student_id)
            except Student.DoesNotExist:
                continue

            Score.objects.update_or_create(
                student_id=student_id,
                section=section,
                score_type='regular',
                defaults={
                    'student_no': student_profile.student_no,
                    'student_name': student_profile.user.name,
                    'class_name': student_profile.class_name,
                    'chapter_no': section.chapter.chapter_no,
                    'chapter_name': section.chapter.title,
                    'section_no': section.section_no,
                    'section_name': section.title,
                    'score': total_score,
                    'score_type': 'regular',
                    'source': 'auto_script',
                    'evaluator': f'教师批改:{request.user.name}',
                    'details': details,
                }
            )
            graded_count += 1

        return Response({
            'code': 200,
            'message': f'批改完成，共提交{graded_count}条成绩',
            'data': {'graded_count': graded_count},
        })
