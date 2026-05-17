from django.db import models
from django.conf import settings


class Course(models.Model):
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('active', '已发布'),
        ('archived', '已归档'),
    )
    name = models.CharField(max_length=100, verbose_name='课程名称')
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='授课教师'
    )
    description = models.TextField(blank=True, verbose_name='课程描述')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'courses'
        verbose_name = '课程'
        verbose_name_plural = '课程'

    def __str__(self):
        return self.name


class Chapter(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='chapters', verbose_name='所属课程')
    chapter_no = models.IntegerField(verbose_name='章序号')
    title = models.CharField(max_length=100, verbose_name='章标题')
    sequence = models.IntegerField(default=0, verbose_name='排序')
    is_visible = models.BooleanField(default=True, verbose_name='是否可见')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'chapters'
        verbose_name = '章'
        verbose_name_plural = '章'
        ordering = ['sequence']

    def __str__(self):
        return f"第{self.chapter_no}章 {self.title}"


class Section(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='sections', verbose_name='所属章')
    section_no = models.IntegerField(verbose_name='节序号')
    title = models.CharField(max_length=100, verbose_name='节标题')
    sequence = models.IntegerField(default=0, verbose_name='排序')
    is_active = models.BooleanField(default=False, verbose_name='是否为当前激活节')
    is_visible = models.BooleanField(default=True, verbose_name='是否可见')
    start_time = models.DateTimeField(null=True, blank=True, verbose_name='开始时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'sections'
        verbose_name = '节'
        verbose_name_plural = '节'
        ordering = ['sequence']

    def __str__(self):
        return f"{self.section_no} {self.title}"
