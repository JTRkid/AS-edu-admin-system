# AS-edu-system

在线教学管理系统，支持课程管理、题目管理、自动评分、成绩管理等功能。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Django 5.0 + Django REST Framework |
| 实时通信 | Django Channels + Daphne (WebSocket) |
| 数据库 | MySQL |
| 缓存/通道层 | Redis |
| 前端 | Vue 3 + Vite + Element Plus |
| 代理 | Nginx |

## 项目目录结构

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

## 服务器环境要求

- Ubuntu 20.04+ / CentOS 7+
- Python 3.10+
- Node.js 18+
- MySQL 8.0+
- Redis 6+
- Nginx

---

## 零、服务器环境安装

以下命令覆盖 Ubuntu 20.04+/22.04/24.04 和 CentOS 7/8/9。

### 0.1 更新系统包

```bash
# Ubuntu
sudo apt update && sudo apt upgrade -y

# CentOS
sudo yum update -y
```

### 0.2 安装 Python 3.10+

**Ubuntu：**

```bash
# Ubuntu 22.04+ 自带 Python 3.10+，直接安装 venv 和 pip
sudo apt install -y python3 python3-venv python3-pip

# Ubuntu 20.04 需要添加 deadsnakes PPA
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.10 python3.10-venv python3.10-dev
```

验证：

```bash
python3 --version   # 应输出 3.10.x 或更高
```

**CentOS：**

```bash
# CentOS 7
sudo yum install -y centos-release-scl
sudo yum install -y rh-python38 rh-python38-python-devel
scl enable rh-python38 bash
# 建议写入 .bashrc 持久化
echo "source /opt/rh/rh-python38/enable" >> ~/.bashrc

# CentOS 8/9
sudo dnf install -y python3 python3-pip python3-devel
```

### 0.3 安装 Node.js 18+

**方法一：NodeSource 官方源（推荐，Ubuntu & CentOS 通用）**

```bash
# Ubuntu / Debian
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# CentOS / RHEL
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs
```

**方法二：nvm 版本管理器（适合多版本切换）**

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.bashrc
nvm install 18
nvm use 18
```

验证：

```bash
node --version    # 应输出 v18.x.x
npm --version     # 应输出 9.x.x 或更高
```

### 0.4 安装 MySQL 8.0+

**Ubuntu：**

```bash
sudo apt install -y mysql-server pkg-config libmysqlclient-dev

# 启动并设置开机自启
sudo systemctl start mysql
sudo systemctl enable mysql

# 运行安全配置（设置 root 密码、删除匿名用户等）
sudo mysql_secure_installation
```

**CentOS：**

```bash
# CentOS 7
sudo yum install -y https://dev.mysql.com/get/mysql80-community-release-el7-3.noarch.rpm
sudo yum install -y mysql-community-server pkgconfig mysql-devel

# CentOS 8/9
sudo dnf install -y https://dev.mysql.com/get/mysql80-community-release-el8-1.noarch.rpm
sudo dnf install -y mysql-community-server pkgconfig mysql-devel

# 启动
sudo systemctl start mysqld
sudo systemctl enable mysqld

# 获取临时密码
sudo grep 'temporary password' /var/log/mysqld.log
sudo mysql_secure_installation
```

验证：

```bash
mysql --version
sudo systemctl status mysql    # Ubuntu
sudo systemctl status mysqld   # CentOS
```

### 0.5 安装 Redis

**Ubuntu：**

```bash
sudo apt install -y redis-server

# 配置 Redis 监听本地
sudo sed -i 's/^bind 127.0.0.1 ::1/bind 127.0.0.1/' /etc/redis/redis.conf

sudo systemctl start redis-server
sudo systemctl enable redis-server
```

**CentOS：**

```bash
# CentOS 7
sudo yum install -y epel-release
sudo yum install -y redis

# CentOS 8/9
sudo dnf install -y redis

# 启动
sudo systemctl start redis
sudo systemctl enable redis
```

验证：

```bash
redis-cli ping   # 应返回 PONG
```

### 0.6 安装 Nginx

**Ubuntu：**

```bash
sudo apt install -y nginx

# 启动
sudo systemctl start nginx
sudo systemctl enable nginx
```

**CentOS：**

```bash
# CentOS 7
sudo yum install -y epel-release
sudo yum install -y nginx

# CentOS 8/9
sudo dnf install -y nginx

# 启动
sudo systemctl start nginx
sudo systemctl enable nginx
```

验证：

```bash
sudo nginx -t                # 检查配置
sudo systemctl status nginx  # 查看状态
curl http://127.0.0.1        # 应返回 Nginx 欢迎页
```

### 0.7 安装 Git

```bash
# Ubuntu
sudo apt install -y git

# CentOS
sudo yum install -y git
```

### 0.8 环境安装完成确认

```bash
python3 --version   # Python 3.10+
node --version      # v18+
npm --version       # 9+
mysql --version     # 8.0+
redis-cli ping      # PONG
nginx -v            # nginx/1.x
git --version       # 2.x+
```

---

## 一、从 GitHub 拉取代码

```bash
cd /home
git clone https://github.com/JTRkid/AS-edu-admin-system.git
cd AS-edu-admin-system
```

---

## 二、后端部署

### 2.1 安装 Python 依赖

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2.2 创建生产环境配置文件

在 `backend/teach_platform/` 目录下创建 `.env` 文件。

首先生成 SECRET_KEY 随机字符串：

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

复制输出的字符串备用，然后创建 `.env` 文件：

```bash
# 手动创建
vim backend/teach_platform/.env
```

`.env` 文件内容（**根据实际情况修改**）：

```ini
# Django 核心
SECRET_KEY=请用下方命令生成随机字符串替换这里
DEBUG=False
ALLOWED_HOSTS=你的域名或服务器IP

# 数据库
DB_NAME=teach_platform
DB_USER=你的数据库用户名
DB_PASSWORD=你的数据库密码
DB_HOST=127.0.0.1
DB_PORT=3306

# Redis (Channels 通道层)
REDIS_HOST=127.0.0.1
REDIS_PORT=6379

# 前端地址 (CORS 白名单)
CORS_ORIGIN=http://你的域名或服务器IP
```

### 2.3 修改 settings.py 读取 .env

确认 `backend/teach_platform/settings.py` 顶部已有以下代码，若没有则添加：

```python
import os
from dotenv import load_dotenv
load_dotenv()
```

然后将硬编码的敏感配置改为从环境变量读取。**需要修改的配置项：**

| 配置项 | 原始值（硬编码） | 改为 |
|--------|------------------|------|
| `SECRET_KEY` | 硬编码字符串 | `os.environ.get('SECRET_KEY')` |
| `DEBUG` | `True` | `os.environ.get('DEBUG', 'False') == 'True'` |
| `ALLOWED_HOSTS` | `['*']` | `os.environ.get('ALLOWED_HOSTS', '').split(',')` |
| 数据库 `USER` | `root` | `os.environ.get('DB_USER')` |
| 数据库 `PASSWORD` | `123456` | `os.environ.get('DB_PASSWORD')` |
| 数据库 `HOST` | `101.126.142.233` | `os.environ.get('DB_HOST', '127.0.0.1')` |
| `CORS_ALLOW_ALL_ORIGINS` | `True` | 删除，改为 `CORS_ALLOWED_ORIGINS = [os.environ.get('CORS_ORIGIN', '')]` |
| Channels 通道层 | `InMemoryChannelLayer` | 改为 Redis（见下方） |

**Channels 通道层改为 Redis（`backend/teach_platform/settings.py` 约第 139 行）：**

```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(os.environ.get("REDIS_HOST", "127.0.0.1"), int(os.environ.get("REDIS_PORT", 6379)))],
        },
    },
}
```

并在 `requirements.txt` 中添加 `channels_redis`：

```bash
echo "channels_redis==4.2.0" >> requirements.txt
pip install channels_redis
```

### 2.4 创建数据库

```bash
mysql -u root -p
```

```sql
CREATE DATABASE teach_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER '你的用户名'@'localhost' IDENTIFIED BY '你的密码';
GRANT ALL PRIVILEGES ON teach_platform.* TO '你的用户名'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 2.5 执行数据库迁移与静态文件收集

```bash
cd backend
source venv/bin/activate

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
```

### 2.6 创建默认管理员（种子数据）

```bash
python seed_data.py
```

> 默认管理员账号：`admin`，密码：`123456`

---

## 三、前端部署

### 3.1 安装依赖

```bash
cd frontend
npm install
```

### 3.2 配置 API 地址

修改 `frontend/src/api/index.js`，将 `baseURL` 改为生产环境地址：

```javascript
// 将 localhost:8000 改为实际后端地址
const api = axios.create({
  baseURL: 'http://你的域名或服务器IP:8000/api/v1',
  // ...
})
```

或者使用相对路径（推荐配合 Nginx 反向代理）：

```javascript
const api = axios.create({
  baseURL: '/api/v1',
  // ...
})
```

### 3.3 构建生产包

```bash
npm run build
```

构建产物在 `frontend/dist/` 目录。

---

## 四、Nginx 配置

创建 Nginx 配置文件：

```bash
sudo vim /etc/nginx/sites-available/as-edu
```

```nginx
server {
    listen 80;
    server_name 你的域名或服务器IP;

    # 前端静态文件
    location / {
        root /home/AS-edu-admin-system/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 反向代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # 后端静态文件 (Django collectstatic)
    location /static/ {
        alias /home/AS-edu-admin-system/backend/staticfiles/;
    }

    # 用户上传文件
    location /media/ {
        alias /home/AS-edu-admin-system/backend/media/;
    }

    # WebSocket 反向代理
    location /ws/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/as-edu /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 五、生产环境后台运行（断开 SSH 不终止）

使用 **systemd** 管理后端进程，确保服务器重启自动拉起、SSH 断开不终止。

### 5.1 Django HTTP 服务 (Gunicorn)

创建 systemd 服务文件：

```bash
sudo vim /etc/systemd/system/as-edu.service
```

```ini
[Unit]
Description=AS-edu-system Django Backend
After=network.target mysql.service redis.service

[Service]
User=root
Group=root
WorkingDirectory=/home/AS-edu-admin-system/backend
EnvironmentFile=/home/AS-edu-admin-system/backend/teach_platform/.env
ExecStart=/home/AS-edu-admin-system/backend/venv/bin/gunicorn teach_platform.wsgi:application \
    --bind 127.0.0.1:8000 \
    --workers 4 \
    --timeout 120 \
    --access-logfile /var/log/as-edu-access.log \
    --error-logfile /var/log/as-edu-error.log
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

> 安装 gunicorn：`pip install gunicorn`

### 5.2 WebSocket 服务 (Daphne)

```bash
sudo vim /etc/systemd/system/as-edu-daphne.service
```

```ini
[Unit]
Description=AS-edu-system WebSocket (Daphne)
After=network.target mysql.service redis.service

[Service]
User=root
Group=root
WorkingDirectory=/home/AS-edu-admin-system/backend
EnvironmentFile=/home/AS-edu-admin-system/backend/teach_platform/.env
ExecStart=/home/AS-edu-admin-system/backend/venv/bin/daphne \
    -b 127.0.0.1 -p 8001 \
    teach_platform.asgi:application
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 5.3 启动服务

```bash
# 重新加载 systemd 配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start as-edu
sudo systemctl start as-edu-daphne

# 设置开机自启
sudo systemctl enable as-edu
sudo systemctl enable as-edu-daphne

# 查看运行状态
sudo systemctl status as-edu
sudo systemctl status as-edu-daphne
```

### 5.4 常用管理命令

```bash
# 查看日志
sudo journalctl -u as-edu -f
sudo journalctl -u as-edu-daphne -f

# 重启服务（代码更新后）
sudo systemctl restart as-edu
sudo systemctl restart as-edu-daphne

# 停止服务
sudo systemctl stop as-edu
sudo systemctl stop as-edu-daphne
```

---

## 六、更新部署流程

代码更新后执行以下步骤：

```bash
cd /home/AS-edu-admin-system
git pull

# 后端
cd backend
source venv/bin/activate
pip install -r requirements.txt   # 如有新依赖
python manage.py migrate          # 如有新迁移
python manage.py collectstatic --noinput
sudo systemctl restart as-edu
sudo systemctl restart as-edu-daphne

# 前端
cd ../frontend
npm install                       # 如有新依赖
npm run build
```

---

## 七、快速部署命令汇总

首次部署完整命令序列：

```bash
# 1. 拉取代码
cd /home
git clone https://github.com/JTRkid/AS-edu-admin-system.git
cd AS-edu-admin-system

# 2. 安装系统依赖
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nodejs npm nginx mysql-server redis-server

# 3. 后端
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn channels_redis

# 4. 创建 .env 配置文件（按实际情况修改）
vim teach_platform/.env

# 5. 数据库
mysql -u root -p <<SQL
CREATE DATABASE teach_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
SQL

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
python seed_data.py

# 6. 前端
cd ../frontend
npm install
npm run build

# 7. Nginx（复制上方 Nginx 配置后）
sudo ln -s /etc/nginx/sites-available/as-edu /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# 8. systemd 服务（复制上方两个 .service 文件后）
sudo systemctl daemon-reload
sudo systemctl enable --now as-edu
sudo systemctl enable --now as-edu-daphne

# 9. 验证
curl http://127.0.0.1:8000/api/v1/
curl http://127.0.0.1/
```

---

## 八、启动项目

### 开发环境启动（本地调试）

**后端：**

```bash
cd backend
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

**前端：**

```bash
cd frontend
npm run dev
```

前端开发服务器默认运行在 `http://localhost:3000`，API 请求自动代理到 `localhost:8000`。

### 生产环境启动

部署完成后，所有服务由 systemd 管理：

```bash
# 启动所有服务
sudo systemctl start mysql
sudo systemctl start redis
sudo systemctl start nginx
sudo systemctl start as-edu
sudo systemctl start as-edu-daphne

# 设置所有服务开机自启
sudo systemctl enable mysql
sudo systemctl enable redis
sudo systemctl enable nginx
sudo systemctl enable as-edu
sudo systemctl enable as-edu-daphne
```

一键启动命令：

```bash
sudo systemctl start mysql redis nginx as-edu as-edu-daphne
```

### 验证服务已启动

```bash
# 检查各服务状态
sudo systemctl status mysql | head -3
sudo systemctl status redis | head -3
sudo systemctl status nginx | head -3
sudo systemctl status as-edu | head -3
sudo systemctl status as-edu-daphne | head -3

# 验证端口监听
sudo ss -tlnp | grep -E '80|8000|8001|3306|6379'

# HTTP 访问验证
curl http://127.0.0.1:8000/api/v1/
curl http://127.0.0.1/
```

浏览器访问 `http://你的服务器IP` 即可打开系统。

---

## 九、端口说明

| 端口 | 服务 | 说明 |
|------|------|------|
| 80 | Nginx | 前端页面 + 反向代理 |
| 8000 | Gunicorn | Django HTTP (仅本地监听) |
| 8001 | Daphne | WebSocket (仅本地监听) |
| 3306 | MySQL | 数据库 |
| 6379 | Redis | 缓存 + Channels 通道层 |

> 云服务器需在安全组中开放 80 端口。8000/8001 仅本地监听，无需对外开放。

---

## 十、实验成绩传送流程

### 整体架构

```
+-------------------+         HTTP POST          +-------------------+
|   学生实验 VM      |  ──────────────────────>  |   教学平台服务器    |
|                   |   /api/v1/scores/submit/   |                   |
|  scripts/test.sh  |    Authorization: ApiKey   |  score_submit_api |
|  (自动评分脚本)    |                            |  (接收 + 存储)     |
+-------------------+                            +--------+----------+
                                                          |
                                                    WebSocket 推送
                                                          |
                                                          v
                                                   +------+------+
                                                   |   学生浏览器   |
                                                   |  实时看到成绩  |
                                                   +-------------+
```

### 流程说明

1. **教师端**：在平台上创建课程 → 章 → 节（如"Python程序设计 → 第1章 Python基础 → 第1节 Python简介"）
2. **学生端**：在虚拟机中完成实验，编写代码文件（如 `hello.py`）
3. **评分脚本**：教师预先编写评分脚本（参考 `scripts/test.sh`），部署到学生虚拟机中
4. **执行评分**：学生运行评分脚本，脚本自动检查代码并打分
5. **成绩回传**：脚本通过 HTTP POST 将成绩发送到教学平台 `/api/v1/scores/submit/`
6. **实时推送**：平台保存成绩后，通过 WebSocket 实时推送到学生浏览器

### API 接口说明

**实验成绩提交接口：**

```
POST /api/v1/scores/submit/
Authorization: ApiKey <SCORING_MACHINE_API_KEY>
Content-Type: application/json
```

**请求体：**

```json
{
    "student_no": "2024001001001",
    "student_name": "张三",
    "class_name": "计算机1班",
    "course_name": "Python程序设计",
    "chapter_no": 1,
    "chapter_name": "Python基础",
    "section_no": 1,
    "section_name": "Python简介与环境搭建",
    "score": 85.0,
    "evaluator": "exp-script-v1",
    "details": "文件检查通过(+20); 语法检查通过(+20); 输出包含Hello(+20); ..."
}
```

**字段说明：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| student_no | string | 是 | 学生学号，需在系统中存在 |
| student_name | string | 是 | 学生姓名 |
| class_name | string | 是 | 班级名称 |
| course_name | string | 否 | 课程名称，用于多课程场景精确匹配节 |
| chapter_no | integer | 是 | 章序号 |
| chapter_name | string | 否 | 章名称 |
| section_no | integer | 是 | 节序号 |
| section_name | string | 否 | 节名称 |
| score | number | 是 | 成绩，0-100 |
| evaluator | string | 否 | 评分机标识，用于追踪来源 |
| details | string | 否 | 评分详情说明 |
| timestamp | datetime | 否 | 评分时间戳 |

**认证方式：**

API 使用 `ApiKey` 认证。请求头需携带：
```
Authorization: ApiKey <密钥>
```

密钥在 `backend/teach_platform/settings.py` 中配置：

```python
SCORING_MACHINE_API_KEY = 'scoring-machine-secret-key-2026'
```

> 生产环境请修改此密钥为强随机字符串。

### 评分脚本示例

参考项目 `scripts/test.sh`，核心结构：

```bash
#!/bin/bash

# --- 配置 ---
PLATFORM_URL="http://127.0.0.1:8000"
API_KEY="scoring-machine-secret-key-2026"
CHAPTER_NO=1
SECTION_NO=1
COURSE_NAME="Python程序设计"

# --- 读取学生信息 ---
read -p "请输入学号: " STUDENT_NO
read -p "请输入姓名: " STUDENT_NAME
read -p "请输入班级: " CLASS_NAME

# --- 评分逻辑 ---
SCORE=0
DETAILS=""

# 检查项1: 文件是否存在
if [ -f "./hello.py" ]; then
    SCORE=$((SCORE + 20))
    DETAILS="${DETAILS}文件检查通过(+20); "
fi

# 检查项2: 语法是否正确
if python3 -m py_compile hello.py 2>/dev/null; then
    SCORE=$((SCORE + 20))
    DETAILS="${DETAILS}语法检查通过(+20); "
fi

# ... 更多评分项 ...

# --- 发送成绩 ---
curl -X POST "${PLATFORM_URL}/api/v1/scores/submit/" \
    -H "Authorization: ApiKey ${API_KEY}" \
    -H "Content-Type: application/json" \
    -d "{
        \"student_no\": \"${STUDENT_NO}\",
        \"student_name\": \"${STUDENT_NAME}\",
        \"class_name\": \"${CLASS_NAME}\",
        \"course_name\": \"${COURSE_NAME}\",
        \"chapter_no\": ${CHAPTER_NO},
        \"section_no\": ${SECTION_NO},
        \"score\": ${SCORE},
        \"evaluator\": \"exp-script-v1\",
        \"details\": \"${DETAILS}\"
    }"

echo "最终成绩: ${SCORE}/100"
```

### 操作步骤

**教师端操作：**

1. 登录教师端 → 课程管理 → 添加课程、章、节
2. 在题目管理中为各节添加实验题目
3. 将 `scripts/test.sh` 评分脚本复制到学生虚拟机，根据实验内容修改评分逻辑
4. 确保脚本中的 `PLATFORM_URL` 和 `API_KEY` 配置正确
5. 通知学生开始实验

**学生端操作：**

1. 登录学生端 → 课程学习 → 选择对应章节查看实验要求
2. 在虚拟机中编写实验代码（如 `hello.py`）
3. 运行评分脚本：
   ```bash
   bash test.sh
   ```
4. 按提示输入学号、姓名、班级
5. 脚本自动评分并提交到平台
6. 刷新学生端"我的成绩"页面查看实验成绩

**成绩查看：**

- **学生**：学生端 → 我的成绩 → 切换"实验成绩"标签查看
- **教师**：教师端 → 成绩管理 → 切换"实验成绩"标签查看、导出

### 成绩覆盖规则

- 同一学生 + 同一节 + 同一成绩类型（`experiment`）= 唯一记录
- 再次提交会**覆盖**旧成绩，旧值保存在 `original_score` 字段中
- 教师可在成绩管理中手动修改，修改记录进入 `ScoreHistory` 审计表
- WebSocket 推送仅对在线学生生效
