from django.db import models


class Question(models.Model):
    TYPE_CHOICES = (
        ('single', '单选题'),
        ('multiple', '多选题'),
        ('judgment', '判断题'),
        ('essay', '简答题'),
    )
    section = models.ForeignKey(
        'courses.Section', on_delete=models.CASCADE, related_name='questions', verbose_name='所属节'
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='题型')
    title = models.TextField(verbose_name='题目标题')
    content = models.TextField(blank=True, verbose_name='题目内容')
    options = models.JSONField(null=True, blank=True, verbose_name='选择题选项')
    correct_answer = models.TextField(blank=True, verbose_name='客观题答案')
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=100.00, verbose_name='满分')
    deadline = models.DateTimeField(null=True, blank=True, verbose_name='答题截止时间')
    allow_resubmit = models.BooleanField(default=True, verbose_name='允许重新提交')
    is_published = models.BooleanField(default=False, verbose_name='是否发布')
    order_num = models.IntegerField(default=0, verbose_name='排序')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'questions'
        verbose_name = '题目'
        verbose_name_plural = '题目'
        ordering = ['order_num']
        unique_together = [('section', 'order_num')]

    def __str__(self):
        return self.title[:50]
