"""答案提交模型定义"""

from django.db import models
from django.conf import settings


class Submission(models.Model):
    """答案提交模型，记录学生对某道题的作答内容和提交时间"""
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='学生'
    )
    question = models.ForeignKey(
        'questions.Question', on_delete=models.CASCADE, verbose_name='题目'
    )
    section = models.ForeignKey(
        'courses.Section', on_delete=models.CASCADE, verbose_name='所属节'
    )
    answer = models.TextField(blank=True, verbose_name='答案内容')
    language = models.CharField(max_length=20, blank=True, verbose_name='编程题语言')
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name='提交时间')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='IP地址')

    class Meta:
        db_table = 'submissions'
        verbose_name = '答案提交'
        verbose_name_plural = '答案提交'
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.student.name} - {self.question.title[:30]}"
