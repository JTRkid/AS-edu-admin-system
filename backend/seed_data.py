"""测试数据填充脚本 — 创建课程、章、节和题目，用于开发和演示"""

import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'teach_platform.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import django
django.setup()

from apps.courses.models import Course, Chapter, Section
from apps.questions.models import Question as Q
from apps.accounts.models import User, Teacher
from django.db.models import Sum
import bcrypt

# 默认管理员账号
admin_pw = bcrypt.hashpw('123456'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
admin, created = User.objects.update_or_create(
    username='admin',
    defaults={'name': '管理员', 'password': admin_pw, 'role': 'admin', 'is_staff': True, 'is_superuser': True},
)
Teacher.objects.update_or_create(
    user=admin,
    defaults={'teacher_no': 'admin', 'department': '管理部', 'is_admin': True},
)
if created:
    print('默认管理员账号已创建 (admin / 123456)')

# 创建默认教师账号（不存在则创建）
teacher_pw = bcrypt.hashpw('123456'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
teacher, _ = User.objects.get_or_create(
    username='t001',
    defaults={'name': '默认教师', 'password': teacher_pw, 'role': 'teacher'},
)
_, teacher_created = Teacher.objects.get_or_create(
    user=teacher,
    defaults={'teacher_no': 't001', 'department': '计算机系'},
)
if teacher_created:
    print('默认教师账号已创建 (t001 / 123456)')

# === Course 1 ===
c1 = Course.objects.create(name='Python程序设计', teacher=teacher, description='零基础学习Python编程', status='active')

ch1 = Chapter.objects.create(course=c1, title='Python基础', chapter_no=1)
s1 = Section.objects.create(chapter=ch1, title='Python简介与环境搭建', section_no=1, is_visible=True)
s2 = Section.objects.create(chapter=ch1, title='变量与数据类型', section_no=2, is_visible=True)

ch2 = Chapter.objects.create(course=c1, title='流程控制', chapter_no=2)
s3 = Section.objects.create(chapter=ch2, title='条件判断', section_no=1, is_visible=True)
s4 = Section.objects.create(chapter=ch2, title='循环语句', section_no=2, is_visible=True)

ch3 = Chapter.objects.create(course=c1, title='函数与模块', chapter_no=3)
s5 = Section.objects.create(chapter=ch3, title='函数定义与调用', section_no=1, is_visible=True)
s6 = Section.objects.create(chapter=ch3, title='模块与包', section_no=2, is_visible=True)

ch4 = Chapter.objects.create(course=c1, title='面向对象编程', chapter_no=4)
s7 = Section.objects.create(chapter=ch4, title='类与对象', section_no=1, is_visible=True)

# === Course 2 ===
c2 = Course.objects.create(name='数据库原理', teacher=teacher, description='关系型数据库与SQL语言', status='active')

ch5 = Chapter.objects.create(course=c2, title='数据库基础', chapter_no=1)
s8 = Section.objects.create(chapter=ch5, title='数据库概述', section_no=1, is_visible=True)
s9 = Section.objects.create(chapter=ch5, title='关系模型', section_no=2, is_visible=True)

ch6 = Chapter.objects.create(course=c2, title='SQL语言', chapter_no=2)
s10 = Section.objects.create(chapter=ch6, title='数据查询(SELECT)', section_no=1, is_visible=True)
s11 = Section.objects.create(chapter=ch6, title='数据操作(INSERT/UPDATE/DELETE)', section_no=2, is_visible=True)

print('2门课程、6章、11节 创建完成')

# === Questions ===
qs = [
    (s1, 'single', 'Python的作者是谁？', ['Guido van Rossum', 'Dennis Ritchie', 'James Gosling', 'Brendan Eich'], 'A', 5),
    (s1, 'single', 'Python是哪种类型的语言？', ['编译型', '解释型', '汇编型', '机器语言'], 'B', 5),
    (s1, 'judgment', 'Python可以跨平台运行', ['正确', '错误'], '正确', 5),
    (s1, 'essay', '简述Python的特点', [], '', 20),

    (s2, 'single', '以下哪个是合法的变量名？', ['2name', '_name', 'class', 'my-name'], 'B', 5),
    (s2, 'multiple', '以下哪些是不可变数据类型？', ['int', 'list', 'tuple', 'str'], 'A,C,D', 10),
    (s2, 'judgment', 'Python中变量不需要声明类型', ['正确', '错误'], '正确', 5),
    (s2, 'essay', '列表和元组的区别', [], '', 15),

    (s3, 'single', 'Python中不等于的运算符是？', ['<>', '!=', '~=', '/='], 'B', 5),
    (s3, 'single', 'x=10;if x>5:print("A")else:print("B") 输出？', ['A', 'B', 'AB', '无输出'], 'A', 5),
    (s3, 'essay', '编写判断闰年的程序', [], '', 20),

    (s4, 'single', 'range(5)生成的序列是？', ['0,1,2,3,4,5', '0,1,2,3,4', '1,2,3,4,5'], 'B', 5),
    (s4, 'multiple', '以下哪些是Python的循环语句？', ['for', 'while', 'do-while', 'loop'], 'A,B', 10),
    (s4, 'judgment', 'break语句可以跳出循环', ['正确', '错误'], '正确', 5),
    (s4, 'essay', '打印九九乘法表', [], '', 20),

    (s5, 'single', '定义函数的关键字是？', ['function', 'def', 'func', 'define'], 'B', 5),
    (s5, 'multiple', '函数的参数传递方式有哪些？', ['位置参数', '关键字参数', '默认参数', '可变参数'], 'A,B,C,D', 10),
    (s5, 'essay', '编写计算阶乘的递归函数', [], '', 20),

    (s6, 'single', '导入数学模块的正确方式是？', ['include math', 'import math', 'using math', 'require math'], 'B', 5),
    (s6, 'judgment', '一个Python文件就是一个模块', ['正确', '错误'], '正确', 5),
    (s6, 'essay', '如何创建自定义模块', [], '', 20),

    (s7, 'single', '类中第一个参数通常是什么？', ['this', 'self', 'that', 'me'], 'B', 5),
    (s7, 'multiple', '面向对象的三大特性是？', ['封装', '继承', '多态', '反射'], 'A,B,C', 10),
    (s7, 'judgment', 'Python支持多重继承', ['正确', '错误'], '正确', 5),
    (s7, 'essay', '设计一个Student类', [], '', 20),

    (s8, 'single', '最主流的关系型数据库是？', ['MongoDB', 'MySQL', 'Redis', 'Elasticsearch'], 'B', 5),
    (s8, 'judgment', 'DBMS就是数据库', ['正确', '错误'], '错误', 5),

    (s9, 'single', '关系模型中一行数据称为？', ['属性', '元组', '域', '关系'], 'B', 5),
    (s9, 'multiple', '数据库完整性约束有哪些？', ['实体完整性', '参照完整性', '用户自定义完整性', '网络完整性'], 'A,B,C', 10),

    (s10, 'single', 'SQL查询语句的关键字是？', ['SELECT', 'QUERY', 'FIND', 'GET'], 'A', 5),
    (s10, 'essay', '写出多表连接查询SQL', [], '', 20),

    (s11, 'single', '插入数据的SQL命令是？', ['ADD', 'INSERT', 'CREATE', 'PUT'], 'B', 5),
    (s11, 'judgment', 'DELETE可以删除表中所有行', ['正确', '错误'], '正确', 5),
]

for i, q in enumerate(qs):
    sec, typ, title, opts, ans, score = q
    content = '请回答：' + title if typ == 'essay' else ''
    Q.objects.create(
        section=sec, type=typ, title=title, content=content,
        options=opts, correct_answer=ans, max_score=score,
        order_num=i + 1, is_published=False,
    )

print(f'\n题目: {Q.objects.count()}道')
for t, n in [('single','单选'),('multiple','多选'),('judgment','判断'),('essay','简答')]:
    print(f'  {n}: {Q.objects.filter(type=t).count()}道')

print('\n各节总分:')
for s in Section.objects.all().order_by('chapter__chapter_no', 'section_no'):
    total = Q.objects.filter(section=s).aggregate(t=Sum('max_score'))['t'] or 0
    flag = ' < 超标!' if total > 100 else ''
    print(f'  [{s.chapter.chapter_no}.{s.section_no} {s.title}] {total}分{flag}')

print('\n全部测试数据生成完成!')
