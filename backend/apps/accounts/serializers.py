import re
import bcrypt
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import User, Student, Teacher, StudentGroup, VerifyCode, OperationLog


class LoginSerializer(serializers.Serializer):
    account = serializers.CharField(max_length=20)
    password = serializers.CharField(max_length=128)

    def validate(self, attrs):
        account = attrs.get('account')
        password = attrs.get('password')

        # Try to find user by student_no or teacher_no
        user = None
        try:
            student = Student.objects.get(student_no=account)
            user = student.user
        except Student.DoesNotExist:
            try:
                teacher = Teacher.objects.get(teacher_no=account)
                user = teacher.user
            except Teacher.DoesNotExist:
                pass

        if user is None:
            raise serializers.ValidationError('账号不存在')

        if not user.is_active:
            raise serializers.ValidationError('账号已被禁用')

        # Verify password using bcrypt
        if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            # Also try Django's built-in check
            if not user.check_password(password):
                raise serializers.ValidationError('密码错误')

        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'phone', 'phone_verified', 'role', 'is_active']


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = Student
        fields = ['user_id', 'student_no', 'class_name', 'group', 'user', 'name']


class StudentCreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=128, write_only=True)

    class Meta:
        model = Student
        fields = ['student_no', 'class_name', 'name', 'password']

    def validate_student_no(self, value):
        if not re.match(r'^\d{13}$', value):
            raise serializers.ValidationError('学号必须为13位数字')
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('该学号已被使用')
        return value

    def validate_class_name(self, value):
        if not re.match(r'^\d{9}$', value):
            raise serializers.ValidationError('班级号必须为9位数字')
        return value

    def create(self, validated_data):
        name = validated_data.pop('name')
        password = validated_data.pop('password')
        student_no = validated_data['student_no']

        username = student_no
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        user = User.objects.create(
            username=username,
            name=name,
            password=hashed_pw,
            role='student',
        )
        student = Student.objects.create(user=user, **validated_data)
        return student


class TeacherSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = Teacher
        fields = ['user_id', 'teacher_no', 'department', 'is_admin', 'user', 'name']


class TeacherCreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=128, write_only=True)

    class Meta:
        model = Teacher
        fields = ['teacher_no', 'department', 'name', 'password']

    def validate_teacher_no(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('该教师号已被使用')
        return value

    def create(self, validated_data):
        name = validated_data.pop('name')
        password = validated_data.pop('password')
        teacher_no = validated_data['teacher_no']

        username = teacher_no
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        user = User.objects.create(
            username=username,
            name=name,
            password=hashed_pw,
            role='teacher',
        )
        teacher = Teacher.objects.create(user=user, **validated_data)
        return teacher


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128)
    new_password = serializers.CharField(max_length=128)

    def validate_new_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError('密码长度不能少于6位')
        return value


class ResetPasswordSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    verify_code = serializers.CharField(max_length=10)
    new_password = serializers.CharField(max_length=128)
    confirm_password = serializers.CharField(max_length=128)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError('两次密码输入不一致')
        if len(attrs['new_password']) < 6:
            raise serializers.ValidationError('密码长度不能少于6位')

        # Verify code
        code = VerifyCode.objects.filter(
            phone=attrs['phone'],
            code=attrs['verify_code'],
            used=False,
            expires_at__gt=timezone.now(),
        ).first()

        if not code:
            raise serializers.ValidationError('验证码无效或已过期')
        if code.attempt_count >= 3:
            raise serializers.ValidationError('验证码尝试次数已达上限')

        code.attempt_count += 1
        code.save()

        # Find user by phone
        user = User.objects.filter(phone=attrs['phone'], phone_verified=True).first()
        if not user:
            raise serializers.ValidationError('该手机号未绑定账号')

        # Check new password != old password
        if bcrypt.checkpw(attrs['new_password'].encode('utf-8'), user.password.encode('utf-8')):
            raise serializers.ValidationError('新密码不能与旧密码相同')

        attrs['user'] = user
        attrs['code_obj'] = code
        return attrs


class PhoneBindSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    verify_code = serializers.CharField(max_length=10)

    def validate_phone(self, value):
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式不正确')
        if User.objects.filter(phone=value, phone_verified=True).exists():
            raise serializers.ValidationError('该手机号已被绑定')
        return value


class StudentGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentGroup
        fields = ['id', 'name', 'teacher', 'created_at']
        read_only_fields = ['teacher']


class OperationLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = OperationLog
        fields = ['id', 'user', 'user_name', 'action', 'target', 'detail', 'ip_address', 'created_at']
