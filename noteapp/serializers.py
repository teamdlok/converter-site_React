from rest_framework import serializers

from noteapp.models import Note, UploadedFile


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ["id", "title", "body", "slug", "category", "created", "updated"]

class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = '__all__'


#Проверяем celery
from .models import ConversionTask

class ConversionTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversionTask
        fields = ['task_id', 'status', 'input_file', 'result_file', 'created_at']
        read_only_fields = ['task_id', 'status', 'result_file', 'created_at']