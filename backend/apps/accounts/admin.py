from django.contrib import admin
from .models import User, Student, Teacher, StudentGroup, VerifyCode, OperationLog

admin.site.register(User)
admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(StudentGroup)
admin.site.register(VerifyCode)
admin.site.register(OperationLog)
