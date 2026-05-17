from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Document
from .serializers import DocumentSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.select_related('uploaded_by').all()
    serializer_class = DocumentSerializer
    filterset_fields = ['section', 'is_visible']

    def perform_create(self, serializer):
        file = self.request.FILES.get('file')
        file_size = file.size if file else 0
        serializer.save(uploaded_by=self.request.user, file_size=file_size)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response({'code': 200, 'data': serializer.data})

    @action(methods=['post'], detail=True)
    def replace(self, request, pk=None):
        """替换PDF文档（版本号+1）"""
        document = self.get_object()
        file = request.FILES.get('file')
        if not file:
            return Response({'code': 400, 'message': '请上传文件'}, status=400)

        document.file = file
        document.file_size = file.size
        document.version += 1
        document.save()
        serializer = DocumentSerializer(document, context={'request': request})
        return Response({'code': 200, 'message': '文档已更新', 'data': serializer.data})

    @action(methods=['post'], detail=True)
    def toggle_visibility(self, request, pk=None):
        document = self.get_object()
        document.is_visible = not document.is_visible
        document.save()
        return Response({'code': 200, 'message': '可见性已切换'})
