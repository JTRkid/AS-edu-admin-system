# AS-edu-system 需求规格说明书

> 版本 1.0 | 2026-05-18

---

## 1. 项目概述

**AS-edu-system** 是一个在线教学管理系统，支持教师创建课程并发布题目、学生在线学习与答题、自动评分与成绩管理。系统分为学生端、教师端、管理员端三个入口，基于角色进行权限控制。

### 技术栈

| 层 | 技术 |
|----|------|
| 后端框架 | Django 5.0 + Django REST Framework |
| 数据库 | MySQL |
| 认证 | JWT（Simple JWT，bcrypt 密码哈希） |
| 实时通信 | Django Channels + WebSocket |
| 前端框架 | Vue 3（Composition API） |
| UI 组件库 | Element Plus |
| 状态管理 | Pinia |
| 构建工具 | Vite |

### 项目目录结构

```
AS-edu-system/
├── backend/                          # Django 后端
│   ├── manage.py                     # Django CLI 入口
│   ├── requirements.txt              # Python 依赖
│   ├── seed_data.py                  # 测试数据填充脚本（含默认管理员创建）
│   ├── media/                        # 文件上传存储目录
│   │   └── documents/                # 文档文件（按年/月组织）
│   ├── teach_platform/               # Django 项目配置
│   │   ├── settings.py               # 配置文件（数据库/JWT/CORS/Channels）
│   │   ├── urls.py                   # 根 URL 路由（/api/v1/）
│   │   ├── asgi.py                   # ASGI 入口（HTTP + WebSocket）
│   │   ├── wsgi.py                   # WSGI 入口
│   │   └── routing.py                # WebSocket 路由配置
│   └── apps/                         # Django 应用
│       ├── accounts/                 # 用户认证与管理
│       │   ├── models.py             # User / Student / Teacher / StudentGroup / VerifyCode / OperationLog
│       │   ├── views.py              # LoginViewSet / UserViewSet / StudentViewSet / TeacherViewSet
│       │   ├── serializers.py        # 序列化器与验证逻辑
│       │   ├── urls.py               # /auth/ 路由注册
│       │   └── migrations/           # 数据库迁移文件
│       ├── courses/                  # 课程/章/节管理
│       │   ├── models.py             # Course / Chapter / Section
│       │   ├── views.py              # CourseViewSet / ChapterViewSet / SectionViewSet
│       │   ├── serializers.py        # 序列化器（含树结构序列化）
│       │   ├── urls.py               # /courses/ 路由注册
│       │   └── migrations/
│       ├── documents/                # 文档管理
│       │   ├── models.py             # Document（FileField，版本号，可见性）
│       │   ├── views.py              # DocumentViewSet（上传/替换/删除/可见性切换）
│       │   ├── serializers.py
│       │   ├── urls.py               # /documents/ 路由注册
│       │   └── migrations/
│       ├── questions/                # 题目管理
│       │   ├── models.py             # Question（四种题型，选项JSON，自动编号）
│       │   ├── views.py              # QuestionViewSet（批改/批量操作/成绩提交）
│       │   ├── serializers.py
│       │   ├── urls.py               # /questions/ 路由注册
│       │   └── migrations/
│       ├── submissions/              # 答案提交
│       │   ├── models.py             # Submission（学生答题记录）
│       │   ├── views.py              # SubmissionViewSet（提交/覆盖/my查询）
│       │   ├── serializers.py
│       │   ├── urls.py               # /submissions/ 路由注册
│       │   └── migrations/
│       └── scores/                   # 成绩管理
│           ├── models.py             # Score（双类型+审计）/ ScoreHistory
│           ├── views.py              # ScoreViewSet（CRUD/Excel/评分机API）
│           ├── serializers.py        # 含评分机提交序列化器
│           ├── urls.py               # /scores/ 路由注册
│           ├── consumers.py          # WebSocket Consumer（成绩推送）
│           └── migrations/
├── frontend/                         # Vue 3 前端
│   ├── index.html                    # HTML 入口（标签页标题：AS-edu-system）
│   ├── package.json                  # 依赖配置
│   ├── vite.config.js                # Vite 配置（端口3000，API代理）
│   └── src/
│       ├── main.js                   # Vue 应用入口（挂载 Pinia + Router）
│       ├── App.vue                   # 根组件
│       ├── api/
│       │   └── index.js              # API 层（Axios实例/拦截器/辅助函数/所有后端API封装）
│       ├── router/
│       │   └── index.js              # 路由配置（三套布局 + 角色守卫）
│       ├── stores/
│       │   └── auth.js               # Pinia 认证 Store（登录/登出/获取用户/Token管理）
│       ├── utils/
│       │   └── constants.js          # 共享常量（题型映射/来源映射/时间格式化）
│       ├── components/
│       │   └── ChangePassword.vue    # 修改密码弹窗（三端复用）
│       ├── layouts/
│       │   ├── StudentLayout.vue     # 学生端布局（课程导航树 + 面包屑 + 菜单）
│       │   ├── TeacherLayout.vue     # 教师端布局（侧边栏4项导航）
│       │   └── AdminLayout.vue       # 管理员端布局（侧边栏3项导航）
│       └── views/
│           ├── Login.vue             # 登录页（学号/教师号登录 + 记住账号）
│           ├── student/
│           │   ├── Dashboard.vue     # 学生仪表盘（文档预览 + 四种题型作答）
│           │   └── MyScores.vue      # 我的成绩（成绩表格）
│           ├── teacher/
│           │   ├── CourseManage.vue  # 课程管理（章-节树 + 文档上传/替换/删除）
│           │   ├── QuestionManage.vue# 题目管理（CRUD + 发布/批改 + 批量操作）
│           │   ├── StudentManage.vue # 学生管理（CRUD + Excel导入/导出）
│           │   └── ScoreManage.vue   # 成绩管理（CRUD + Excel + 修改审计）
│           └── admin/
│               ├── Monitor.vue       # 服务监控（状态卡片 + 统计 + 日志时间轴）
│               ├── TeacherManage.vue # 教师管理（CRUD + 管理员任免 + 启停）
│               └── OperationLogs.vue # 操作日志（分页只读表格）
└── scripts/
    └── test.sh                       # 实验评分机测试脚本
```

---

## 2. 角色与权限

### 2.1 角色定义

| 角色 | 标识 | 说明 |
|------|------|------|
| 学生 | `student` | 查看课程文档、在线答题、查看个人成绩 |
| 教师 | `teacher` | 管理课程/章/节/题目/文档、管理学生、批改与成绩管理 |
| 管理员 | `admin` | 教师账号管理、管理员任免、操作日志查看 |

### 2.2 权限矩阵

| 功能 | 学生 | 教师 | 管理员 |
|------|:---:|:---:|:---:|
| 登录/修改密码 | ✓ | ✓ | ✓ |
| 浏览课程文档 | ✓ | ✓ | — |
| 在线答题 | ✓ | — | — |
| 查看我的成绩 | ✓ | — | — |
| 课程/章/节管理 | — | ✓ | — |
| 文档上传/替换/删除 | — | ✓ | — |
| 题目管理（CRUD/发布/批量） | — | ✓ | — |
| 学生管理（CRUD/导入导出） | — | ✓ | — |
| 成绩管理（CRUD/导入导出） | — | ✓ | — |
| 教师管理 | — | — | ✓ |
| 管理员任免 | — | — | ✓ |
| 操作日志 | — | — | ✓ |

---

## 3. 功能需求

### 3.1 登录模块

- 使用学号或教师号 + 密码登录
- JWT 双 Token 机制：access_token（2h）+ refresh_token（7d）
- 登录页支持"记住账号"（localStorage 持久化学号/教师号）
- 登录成功后根据角色自动跳转对应端：学生→`/student`，教师→`/teacher`，管理员→`/admin`
- 401 时自动尝试 refresh_token 刷新，失败则跳转登录页

### 3.2 学生端

#### 3.2.1 课程学习
- 左侧课程导航树：课程 → 章 → 节（仅显示可见节）
- 点击节后在右侧显示课程内容
- **文档内容**标签页：PDF 在线预览（iframe），支持多文档切换与下载
- **问答内容**标签页：四种题型（单选/多选/判断/简答）作答
  - 单选题：el-radio 选项
  - 多选题：el-checkbox 选项
  - 判断题：正确/错误 radio
  - 简答题：textarea 输入
- 截止时间到达后答案锁定不允许修改
- 允许重新提交的题目可覆盖旧答案

#### 3.2.2 我的成绩
- 表格展示本人所有课程节对应成绩
- 列：章号、章名、节号、节名、成绩、类型（总成绩/实验）、来源、评分方、时间
- 及格（≥60）绿色显示，不及格红色显示

#### 3.2.3 修改密码
- 下拉菜单进入修改密码弹窗
- 验证旧密码 + 新密码（≥6位）+ 确认密码一致性

### 3.3 教师端

#### 3.3.1 课程管理
- 课程卡片列表，展示章-节树结构
- 课程 CRUD（创建/编辑/删除）
- 章 CRUD（创建/编辑/删除）
- 节 CRUD（创建/编辑/删除），每节关联文档和题目
- 文档管理：上传 PDF / 替换（版本号+1）/ 删除（同时删除物理文件）/ 切换可见性

#### 3.3.2 题目管理
- 选择课程 → 选择节 → 查看该节题目列表
- 题目 CRUD（创建/编辑/删除）
- 四种题型：单选、多选、判断、简答
- 单题操作：发布/撤回
- 批量操作：批量发布、批量撤回、批量设置截止时间、批量删除
- 批改功能：
  - 客观题（单选/多选/判断）自动对比正确答案评分
  - 简答题教师手动打分
  - 按学号汇总展示总分
- 每节总分实时计算，超过 100 分显示警告
- 提交节下总成绩（调用 section_grade 接口）

#### 3.3.3 学生管理
- 学生列表表格（学号/姓名/班级/状态），支持搜索和班级筛选
- 学生 CRUD（添加/编辑/删除）
- 添加学生时验证：学号 13 位数字、班级 9 位数字
- Excel 批量导入（逐行校验，默认密码 123456）
- 导出学生名单为 Excel
- 下载学生导入模板
- 重置学生密码为 123456

#### 3.3.4 成绩管理
- 总成绩 / 实验成绩类型切换
- 按节筛选成绩
- 成绩操作：添加、修改（记录审计历史）、删除、批量删除
- Excel 导出成绩 / 导入成绩 / 下载导入模板
- 成绩修改时通过 ScoreHistory 记录变更前后值和修改原因

#### 3.3.5 修改密码
- 同学生端

### 3.4 管理员端

#### 3.4.1 服务监控
- 服务状态卡片：MySQL 状态、Django 后端状态、WebSocket 服务状态
- 数据统计卡片：用户统计、课程统计、成绩与提交统计
- 系统日志时间轴（最近操作记录）

#### 3.4.2 教师管理
- 教师列表表格（教师号/姓名/部门/管理员状态/启停状态），支持搜索
- 添加教师（默认密码 123456）
- 设为管理员 / 撤销管理员
- 重置密码为 123456
- 启用 / 禁用教师账号

#### 3.4.3 操作日志
- 分页表格展示所有操作日志
- 列：操作人、操作类型、操作对象、详情、IP 地址、操作时间
- 只读查看

#### 3.4.4 修改密码
- 同学生端

---

## 4. 数据库设计

### 4.1 用户相关表

#### users（用户表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT PK | AUTO_INCREMENT | 主键 |
| username | VARCHAR(150) | UNIQUE, NOT NULL | 登录账号（学号/教师号） |
| password | VARCHAR(128) | NOT NULL | bcrypt 加密 |
| name | VARCHAR(50) | NOT NULL | 姓名 |
| role | VARCHAR(10) | NOT NULL | admin / teacher / student |
| phone | VARCHAR(20) | NULL | 手机号 |
| phone_verified | TINYINT(1) | DEFAULT 0 | 手机号已验证 |
| is_active | TINYINT(1) | DEFAULT 1 | 账号启用 |
| is_staff | TINYINT(1) | — | Django Admin 权限（继承） |
| is_superuser | TINYINT(1) | — | Django 超级用户（继承） |
| last_login | DATETIME | NULL | 最后登录时间 |
| date_joined | DATETIME | NOT NULL | 创建时间 |

#### students（学生表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| user_id | BIGINT PK | FK → users.id | 关联用户 |
| student_no | VARCHAR(20) | UNIQUE | 学号（13位数字） |
| class_name | VARCHAR(50) | NOT NULL | 班级（9位数字） |
| group_id | BIGINT | FK → student_groups.id, NULL | 所属分组 |

#### teachers（教师表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| user_id | BIGINT PK | FK → users.id | 关联用户 |
| teacher_no | VARCHAR(20) | UNIQUE | 教师号 |
| department | VARCHAR(50) | NULL | 所属部门 |
| is_admin | TINYINT(1) | DEFAULT 0 | 是否为管理员 |

#### student_groups（学生分组表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT PK | AUTO_INCREMENT | 主键 |
| name | VARCHAR(50) | NOT NULL | 分组名称 |
| teacher_id | BIGINT | FK → users.id | 所属教师 |
| created_at | DATETIME | NOT NULL | 创建时间 |

#### verify_codes（验证码表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT PK | AUTO_INCREMENT | 主键 |
| phone | VARCHAR(20) | NOT NULL | 手机号 |
| code | VARCHAR(10) | NOT NULL | 验证码 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| expires_at | DATETIME | NOT NULL | 过期时间 |
| used | TINYINT(1) | DEFAULT 0 | 已使用 |
| attempt_count | INT | DEFAULT 0 | 尝试验证次数 |

#### operation_logs（操作日志表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT PK | AUTO_INCREMENT | 主键 |
| user_id | BIGINT | FK → users.id | 操作人 |
| action | VARCHAR(50) | NOT NULL | 操作类型 |
| target | VARCHAR(255) | — | 操作对象 |
| detail | TEXT | — | 详情 |
| ip_address | VARCHAR(39) | NULL | IP 地址 |
| created_at | DATETIME | NOT NULL | 操作时间 |

### 4.2 课程相关表

#### courses（课程表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT PK | AUTO_INCREMENT | 主键 |
| name | VARCHAR(100) | NOT NULL | 课程名称 |
| teacher_id | BIGINT | FK → users.id | 授课教师 |
| description | TEXT | — | 课程描述 |
| status | VARCHAR(10) | DEFAULT 'draft' | draft / active / archived |
| created_at | DATETIME | NOT NULL | 创建时间 |

#### chapters（章表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT PK | AUTO_INCREMENT | 主键 |
| course_id | BIGINT | FK → courses.id, CASCADE | 所属课程 |
| chapter_no | INT | NOT NULL | 章序号 |
| title | VARCHAR(100) | NOT NULL | 章标题 |
| sequence | INT | DEFAULT 0 | 排序 |
| is_visible | TINYINT(1) | DEFAULT 1 | 是否可见 |
| created_at | DATETIME | NOT NULL | 创建时间 |

#### sections（节表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT PK | AUTO_INCREMENT | 主键 |
| chapter_id | BIGINT | FK → chapters.id, CASCADE | 所属章 |
| section_no | INT | NOT NULL | 节序号 |
| title | VARCHAR(100) | NOT NULL | 节标题 |
| sequence | INT | DEFAULT 0 | 排序 |
| is_active | TINYINT(1) | DEFAULT 0 | 当前激活节（同课程唯一） |
| is_visible | TINYINT(1) | DEFAULT 1 | 是否可见 |
| start_time | DATETIME | NULL | 开放时间 |
| end_time | DATETIME | NULL | 截止时间 |
| created_at | DATETIME | NOT NULL | 创建时间 |

### 4.3 文档表

#### documents（文档表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT PK | AUTO_INCREMENT | 主键 |
| section_id | BIGINT | FK → sections.id, CASCADE | 所属节 |
| title | VARCHAR(100) | NOT NULL | 文档标题 |
| file | VARCHAR(255) | NOT NULL | 文件路径（FileField） |
| file_size | BIGINT | DEFAULT 0 | 文件大小（字节） |
| uploaded_by_id | BIGINT | FK → users.id | 上传者 |
| version | INT | DEFAULT 1 | 版本号 |
| is_visible | TINYINT(1) | DEFAULT 1 | 是否可见 |
| created_at | DATETIME | NOT NULL | 创建时间 |

### 4.4 题目表

#### questions（题目表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT PK | AUTO_INCREMENT | 主键 |
| section_id | BIGINT | FK → sections.id, CASCADE | 所属节 |
| type | VARCHAR(20) | NOT NULL | single / multiple / judgment / essay |
| title | TEXT | NOT NULL | 题目标题 |
| content | TEXT | — | 题目内容 |
| options | JSON | NULL | 选择题选项数组 |
| correct_answer | TEXT | — | 客观题正确答案 |
| max_score | DECIMAL(5,2) | DEFAULT 100.00 | 满分 |
| deadline | DATETIME | NULL | 截止时间 |
| allow_resubmit | TINYINT(1) | DEFAULT 1 | 允许重新提交 |
| is_published | TINYINT(1) | DEFAULT 0 | 已发布 |
| order_num | INT | DEFAULT 0 | 排序号 |
| created_at | DATETIME | NOT NULL | 创建时间 |

约束：`UNIQUE(section_id, order_num)`

### 4.5 提交表

#### submissions（提交表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT PK | AUTO_INCREMENT | 主键 |
| student_id | BIGINT | FK → users.id | 学生 |
| question_id | BIGINT | FK → questions.id | 题目 |
| section_id | BIGINT | FK → sections.id | 所属节 |
| answer | TEXT | NOT NULL | 答案内容 |
| language | VARCHAR(20) | — | 预留字段 |
| submitted_at | DATETIME | NOT NULL | 提交时间 |
| ip_address | VARCHAR(39) | NULL | IP 地址 |

### 4.6 成绩表

#### scores（成绩表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT PK | AUTO_INCREMENT | 主键 |
| student_id | BIGINT | FK → users.id | 学生 |
| student_no | VARCHAR(20) | NOT NULL | 学号（冗余） |
| class_name | VARCHAR(50) | — | 班级（冗余） |
| student_name | VARCHAR(50) | — | 姓名（冗余） |
| chapter_no | INT | NOT NULL | 章号 |
| chapter_name | VARCHAR(100) | — | 章名 |
| section_no | INT | NOT NULL | 节号 |
| section_name | VARCHAR(100) | — | 节名 |
| section_id | BIGINT | FK → sections.id | 所属节 |
| score | DECIMAL(6,2) | NOT NULL | 成绩 |
| score_type | VARCHAR(20) | DEFAULT 'regular' | regular（总成绩）/ experiment（实验成绩） |
| source | VARCHAR(20) | DEFAULT 'auto_script' | auto_script / manual / import / experiment |
| evaluator | VARCHAR(100) | — | 评分机标识 / 教师姓名 |
| details | TEXT | — | 评分详情 |
| original_score | DECIMAL(6,2) | NULL | 修改前的原始分数 |
| modified_by_id | BIGINT | FK → users.id, NULL | 修改人 |
| modified_at | DATETIME | NULL | 修改时间 |
| modify_reason | VARCHAR(255) | — | 修改原因 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

约束：`UNIQUE(student_id, section_id, score_type)`

#### score_history（成绩修改历史表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT PK | AUTO_INCREMENT | 主键 |
| score_record_id | BIGINT | FK → scores.id, CASCADE | 关联成绩 |
| old_score | DECIMAL(6,2) | NOT NULL | 原分数 |
| new_score | DECIMAL(6,2) | NOT NULL | 新分数 |
| modified_by_id | BIGINT | FK → users.id | 修改人 |
| reason | VARCHAR(255) | — | 修改原因 |
| modified_at | DATETIME | NOT NULL | 修改时间 |

---

## 5. API 设计

基础 URL：`http://localhost:8000/api/v1`

认证方式：JWT Bearer Token（请求头 `Authorization: Bearer <access_token>`）

### 5.1 认证接口（`/auth/`）

| 方法 | 端点 | 说明 | 认证 |
|------|------|------|:---:|
| POST | `/auth/login/` | 登录 | — |
| POST | `/auth/token/refresh/` | 刷新 Token | — |
| POST | `/auth/verify-code/send/` | 发送短信验证码（开发模式返回 123456） | — |
| GET | `/auth/user/me/` | 获取当前用户信息 | JWT |
| PUT | `/auth/user/change-password/` | 修改密码（旧密码+新密码） | JWT |
| POST | `/auth/user/bind-phone/` | 绑定手机号 | JWT |

#### POST /auth/login/

请求体：
```json
{
  "account": "2023001",
  "password": "123456"
}
```

响应：
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "user": {
      "id": 1,
      "name": "张三",
      "role": "student",
      "student_no": "2023001",
      "class_name": "计算机1班"
    }
  }
}
```

### 5.2 学生管理接口（`/auth/students/`）

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/auth/students/` | 学生列表（分页，搜索 search，筛选 class_name） |
| POST | `/auth/students/` | 添加学生 |
| PATCH | `/auth/students/{id}/` | 编辑学生 |
| DELETE | `/auth/students/{id}/` | 删除学生 |
| POST | `/auth/students/{id}/reset_password/` | 重置密码（默认 123456） |
| POST | `/auth/students/batch_import/` | Excel 批量导入 |
| GET | `/auth/students/export_excel/` | 导出 Excel |
| GET | `/auth/students/download_template/` | 下载导入模板 |

### 5.3 教师管理接口（`/auth/teachers/`）

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/auth/teachers/` | 教师列表 |
| POST | `/auth/teachers/` | 添加教师 |
| POST | `/auth/teachers/{id}/set_admin/` | 设为管理员 |
| POST | `/auth/teachers/{id}/revoke_admin/` | 撤销管理员 |
| POST | `/auth/teachers/{id}/toggle_active/` | 启用/禁用 |
| POST | `/auth/teachers/{id}/reset_password/` | 重置密码 |

### 5.4 课程接口（`/courses/`）

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/courses/` | 课程列表 |
| POST | `/courses/` | 创建课程 |
| PATCH | `/courses/{id}/` | 编辑课程 |
| DELETE | `/courses/{id}/` | 删除课程 |
| GET | `/courses/{id}/tree/` | 获取课程章-节树结构 |
| GET | `/courses/simple/` | 课程简单列表（下拉用） |

### 5.5 章接口（`/courses/chapters/`）

| 方法 | 端点 | 说明 |
|------|------|------|
| GET/POST | `/courses/chapters/` | 列表/创建 |
| PATCH/DELETE | `/courses/chapters/{id}/` | 编辑/删除 |

### 5.6 节接口（`/courses/sections/`）

| 方法 | 端点 | 说明 |
|------|------|------|
| GET/POST | `/courses/sections/` | 列表/创建 |
| PATCH/DELETE | `/courses/sections/{id}/` | 编辑/删除 |
| POST | `/courses/sections/{id}/set_active/` | 设为当前激活节 |
| GET | `/courses/sections/active/` | 获取当前激活节 |

### 5.7 文档接口（`/documents/`）

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/documents/` | 文档列表（筛选 section, is_visible） |
| POST | `/documents/` | 上传文档（multipart/form-data） |
| DELETE | `/documents/{id}/` | 删除文档（同时删除物理文件） |
| POST | `/documents/{id}/replace/` | 替换文档（版本号+1，删除旧文件） |
| POST | `/documents/{id}/toggle_visibility/` | 切换可见性 |

### 5.8 题目接口（`/questions/`）

| 方法 | 端点 | 说明 |
|------|------|------|
| GET/POST | `/questions/` | 列表/创建 |
| PATCH/DELETE | `/questions/{id}/` | 编辑/删除 |
| POST | `/questions/{id}/publish/` | 发布题目 |
| POST | `/questions/{id}/unpublish/` | 撤回题目 |
| POST | `/questions/batch_publish/` | 批量发布 |
| POST | `/questions/batch_unpublish/` | 批量撤回 |
| POST | `/questions/batch_deadline/` | 批量设置截止时间 |
| POST | `/questions/batch_delete/` | 批量删除 |
| GET | `/questions/{id}/submissions/` | 获取题目所有提交 |
| POST | `/questions/{id}/grade/` | 教师批改单题 |
| GET | `/questions/section_submissions/` | 获取节下所有提交（按学号分组） |
| GET | `/questions/section_total/` | 获取节下题目总分 |
| POST | `/questions/section_grade/` | 提交节下总成绩 |

### 5.9 提交接口（`/submissions/`）

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/submissions/` | 提交列表（学生仅看自己） |
| POST | `/submissions/` | 提交答案（已有提交则覆盖） |
| GET | `/submissions/my/` | 查看自己的提交记录 |

### 5.10 成绩接口（`/scores/`）

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/scores/` | 成绩列表（筛选 section/chapter_no/score_type/source 等） |
| POST | `/scores/` | 添加成绩 |
| PATCH | `/scores/{id}/` | 编辑成绩 |
| DELETE | `/scores/{id}/` | 删除成绩 |
| PUT | `/scores/{id}/modify/` | 修改成绩（记录审计历史） |
| GET | `/scores/my_scores/` | 学生查看自己的成绩 |
| GET | `/scores/export_excel/` | 导出 Excel |
| POST | `/scores/import_excel/` | 导入 Excel |
| GET | `/scores/download_template/` | 下载导入模板 |
| POST | `/scores/submit/` | 评分机提交成绩（ApiKey 认证） |

### 5.11 WebSocket

| 端点 | 说明 |
|------|------|
| `ws/scores/` | 成绩更新推送，按 `user_id` 分组，事件类型 `score.update` |

### 5.12 评分机 API

`POST /api/v1/scores/submit/`

- 认证方式：Header `Authorization: ApiKey <API_KEY>`
- 按 `student_no` + `chapter_no` + `section_no` + `course_name` 定位节
- 已有成绩则覆盖（实验成绩类型），新增则创建
- 成功后通过 WebSocket 推送成绩更新消息

---

## 6. 前端路由结构

| 路径 | 页面 | 角色 |
|------|------|:---:|
| `/login` | 登录页 | 公开 |
| `/student/dashboard` | 课程学习 | 学生 |
| `/student/scores` | 我的成绩 | 学生 |
| `/teacher/courses` | 课程管理 | 教师 |
| `/teacher/questions` | 题目管理 | 教师 |
| `/teacher/students` | 学生管理 | 教师 |
| `/teacher/scores` | 成绩管理 | 教师 |
| `/admin/dashboard` | 服务监控 | 管理员 |
| `/admin/teachers` | 教师管理 | 管理员 |
| `/admin/logs` | 操作日志 | 管理员 |

路由守卫：未登录跳转 `/login`，角色不匹配拒绝访问（admin 可访问所有路由）。

---

## 7. 部署说明

### 7.1 环境要求

- Python 3.10+
- Node.js 18+
- MySQL 5.7+

### 7.2 后端部署

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python seed_data.py          # 填充测试数据 + 创建默认管理员
python manage.py runserver 0.0.0.0:8000
```

### 7.3 前端部署

```bash
cd frontend
npm install
npm run dev                  # 开发模式，端口 3000
npm run build                # 生产构建
```

### 7.4 默认账号

运行 `seed_data.py` 后自动创建：

| 角色 | 账号 | 密码 |
|------|------|------|
| 管理员 | `admin` | `123456` |
| 教师 | `t001` | `123456` |
| 学生 | 见 seed_data.py 导入的学生 | `123456` |

### 7.5 关键配置

- 后端端口：`8000`
- 前端开发端口：`3000`
- Vite 代理：`/api` → `localhost:8000`
- 验证码开发模式：固定 `123456`

---

## 8. 已知技术债

| # | 位置 | 问题 |
|---|------|------|
| 1 | `scores/views.py:212` | `original_score` 在覆盖前应先保存旧值，当前逻辑先赋值再保存旧值 |
| 2 | `submissions/views.py:19-33` | `perform_create` 为死代码，`create()` 已覆盖提交逻辑 |
| 3 | `submissions/serializers.py` | `get_student_no` 存在 N+1 查询问题 |
| 4 | `TeacherLayout.vue` / `AdminLayout.vue` | 脚本部分 >90% 重复，建议抽取为通用布局组件 |
| 5 | `settings.py` | SECRET_KEY、数据库密码、CORS 等硬编码，生产环境需改用环境变量 |

---

## 9. 变更历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0 | 2026-05-18 | 初始版本，覆盖全部已实现功能 |
