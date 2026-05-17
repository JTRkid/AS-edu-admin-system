#!/bin/bash
source venv/Scripts/activate
cd backend
echo "启动 Django 后端服务 (端口 8000)..."
python manage.py runserver 0.0.0.0:8000
