"""项目根 URL 路由配置"""

from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from django.views.decorators.clickjacking import xframe_options_exempt

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/courses/', include('apps.courses.urls')),
    path('api/v1/documents/', include('apps.documents.urls')),
    path('api/v1/questions/', include('apps.questions.urls')),
    path('api/v1/submissions/', include('apps.submissions.urls')),
    path('api/v1/scores/', include('apps.scores.urls')),
]

if settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', xframe_options_exempt(serve), {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]
