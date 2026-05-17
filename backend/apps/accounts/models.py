from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', '管理员'),
        ('teacher', '教师'),
        ('student', '学生'),
    )
    name = models.CharField(max_length=50, verbose_name='姓名')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='手机号')
    phone_verified = models.BooleanField(default=False, verbose_name='手机号已验证')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')

    username = models.CharField(max_length=150, unique=True, blank=False)

    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return self.username


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    student_no = models.CharField(max_length=20, unique=True, verbose_name='学号')
    class_name = models.CharField(max_length=50, verbose_name='班级')
    group = models.ForeignKey(
        'StudentGroup', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='分组'
    )

    class Meta:
        db_table = 'students'
        verbose_name = '学生'
        verbose_name_plural = '学生'

    def __str__(self):
        return f"{self.student_no} - {self.user.name if hasattr(self, 'user') else ''}"


class StudentGroup(models.Model):
    name = models.CharField(max_length=50, verbose_name='分组名称')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='所属教师')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'student_groups'
        verbose_name = '学生分组'
        verbose_name_plural = '学生分组'

    def __str__(self):
        return self.name


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    teacher_no = models.CharField(max_length=20, unique=True, verbose_name='教师号')
    department = models.CharField(max_length=50, blank=True, null=True, verbose_name='所属部门')
    is_admin = models.BooleanField(default=False, verbose_name='是否为管理员')

    class Meta:
        db_table = 'teachers'
        verbose_name = '教师'
        verbose_name_plural = '教师'

    def __str__(self):
        return f"{self.teacher_no}"


class VerifyCode(models.Model):
    phone = models.CharField(max_length=20, verbose_name='手机号')
    code = models.CharField(max_length=10, verbose_name='验证码')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    expires_at = models.DateTimeField(verbose_name='过期时间')
    used = models.BooleanField(default=False, verbose_name='已使用')
    attempt_count = models.IntegerField(default=0, verbose_name='尝试次数')

    class Meta:
        db_table = 'verify_codes'
        verbose_name = '验证码'
        verbose_name_plural = '验证码'


class OperationLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='操作人')
    action = models.CharField(max_length=50, verbose_name='操作类型')
    target = models.CharField(max_length=255, blank=True, verbose_name='操作对象')
    detail = models.TextField(blank=True, verbose_name='详情')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='IP地址')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')

    class Meta:
        db_table = 'operation_logs'
        verbose_name = '操作日志'
        verbose_name_plural = '操作日志'
