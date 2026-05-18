"""WSGI 入口 — 传统 HTTP 部署入口"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'teach_platform.settings')
application = get_wsgi_application()
