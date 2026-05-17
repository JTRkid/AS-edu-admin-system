from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import LoginViewSet, UserViewSet, StudentViewSet, TeacherViewSet, StudentGroupViewSet, OperationLogViewSet

router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='student')
router.register(r'teachers', TeacherViewSet, basename='teacher')
router.register(r'groups', StudentGroupViewSet, basename='group')
router.register(r'logs', OperationLogViewSet, basename='log')

urlpatterns = [
    path('login/', LoginViewSet.as_view({'post': 'login'}), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('password/reset/', LoginViewSet.as_view({'post': 'reset_password'}), name='reset_password'),
    path('verify-code/send/', LoginViewSet.as_view({'post': 'send_verify_code'}), name='send_verify_code'),
    path('user/me/', UserViewSet.as_view({'get': 'me'}), name='user_me'),
    path('user/change-password/', UserViewSet.as_view({'put': 'change_password'}), name='change_password'),
    path('user/bind-phone/', UserViewSet.as_view({'post': 'bind_phone'}), name='bind_phone'),
    path('', include(router.urls)),
]
