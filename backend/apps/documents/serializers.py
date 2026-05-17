from rest_framework import serializers
from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.name', read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ['uploaded_by', 'file_size', 'version', 'created_at']

    def get_file_url(self, obj):
        if obj.file:
            return self.context['request'].build_absolute_uri(obj.file.url)
        return None
