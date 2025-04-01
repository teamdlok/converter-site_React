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