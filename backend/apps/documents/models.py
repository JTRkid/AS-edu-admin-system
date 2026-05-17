from django.db import models
from django.conf import settings


class Document(models.Model):
    section = models.ForeignKey(
        'courses.Section', on_delete=models.CASCADE, related_name='documents', verbose_name='所属节'
    )
    title = models.CharField(max_length=100, verbose_name='文档标题')
    file = models.FileField(upload_to='documents/%Y/%m/', verbose_name='文件')
    file_size = models.BigIntegerField(default=0, verbose_name='文件大小')
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='上传者'
    )
    version = models.IntegerField(default=1, verbose_name='版本号')
    is_visible = models.BooleanField(default=True, verbose_name='是否可见')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'documents'
        verbose_name = '文档'
        verbose_name_plural = '文档'

    def __str__(self):
        return self.title
