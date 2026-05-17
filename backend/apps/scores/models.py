from django.db import models
from django.conf import settings


class Score(models.Model):
    SOURCE_CHOICES = (
        ('auto_script', '自动评分'),
        ('manual', '手动录入'),
        ('import', 'Excel导入'),
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='学生'
    )
    student_no = models.CharField(max_length=20, verbose_name='学号（冗余）')
    class_name = models.CharField(max_length=50, blank=True, verbose_name='班级（冗余）')
    student_name = models.CharField(max_length=50, blank=True, verbose_name='姓名（冗余）')
    chapter_no = models.IntegerField(verbose_name='章号')
    chapter_name = models.CharField(max_length=100, blank=True, verbose_name='章名')
    section_no = models.IntegerField(verbose_name='节号')
    section_name = models.CharField(max_length=100, blank=True, verbose_name='节名')
    section = models.ForeignKey(
        'courses.Section', on_delete=models.CASCADE, verbose_name='所属节'
    )
    score = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='成绩')
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='auto_script', verbose_name='来源')
    evaluator = models.CharField(max_length=100, blank=True, verbose_name='评分机标识/教师')
    details = models.TextField(blank=True, verbose_name='评分详情')

    original_score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='原始分数')
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='modified_scores', verbose_name='修改人'
    )
    modified_at = models.DateTimeField(null=True, blank=True, verbose_name='修改时间')
    modify_reason = models.CharField(max_length=255, blank=True, verbose_name='修改原因')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'scores'
        verbose_name = '成绩'
        verbose_name_plural = '成绩'
        unique_together = [('student', 'section')]
        ordering = ['chapter_no', 'section_no', 'student_no']

    def __str__(self):
        return f"{self.student_no} - {self.section_name}: {self.score}"


class ScoreHistory(models.Model):
    score_record = models.ForeignKey(
        Score, on_delete=models.CASCADE, related_name='history', verbose_name='成绩记录'
    )
    old_score = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='原分数')
    new_score = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='新分数')
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='修改人'
    )
    reason = models.CharField(max_length=255, blank=True, verbose_name='修改原因')
    modified_at = models.DateTimeField(auto_now_add=True, verbose_name='修改时间')

    class Meta:
        db_table = 'score_history'
        verbose_name = '成绩修改历史'
        verbose_name_plural = '成绩修改历史'
