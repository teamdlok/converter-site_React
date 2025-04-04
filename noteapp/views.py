import logging
import uuid
from datetime import timedelta
from django.shortcuts import render
from minio import S3Error
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.views import APIView

from converter_site_React import settings
from noteapp.models import Note
from noteapp.serializers import NoteSerializer, FileUploadSerializer
from rest_framework.decorators import api_view
from utils.minio_client import get_minio_client

logger = logging.getLogger(__name__)


from rest_framework import generics, status
from rest_framework.response import Response
from .models import ConversionTask
from .serializers import ConversionTaskSerializer
from .tasks import process_file_task
import uuid

@api_view(['GET'])
def search_notes(request):
    query = request.query_params.get("search")
    notes = Note.objects.filter(Q(title__icontains=query) | Q(body__icontains=query) | Q(category__icontains=query))
    serializer = NoteSerializer(notes, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["GET", "POST"])
def notes(request):
    if request.method == "GET":
        notes = Note.objects.all()
        serializer = NoteSerializer(notes, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = NoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
def note_detail(request, *args, **kwargs):
    try:
        note = Note.objects.get(slug=kwargs.get("slug", None))
    except Note.DoesNotExist:
        return  Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = NoteSerializer(note, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "PUT":
        serializer = NoteSerializer(data=request.data, instance=note)
        if serializer.is_valid():
            serializer.save()
            return Response({"post": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        try:
            note.delete()
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response({"post": f"Note {kwargs.get('slug')} deleted"}, status=status.HTTP_204_NO_CONTENT)


class FileUploadView(APIView):
    def post(self,request, *args,**kwargs):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GeneratePresignedURL(APIView):

    def post(self, request):
        file_name = request.data.get('file_name', str(uuid.uuid4()))

        try:
            minio_client = get_minio_client()
            presigned_url = minio_client.presigned_put_object(
                settings.MINIO_BUCKET_NAME,
                file_name,
                expires=timedelta(hours=1))



            return Response({
                "presigned_url": presigned_url,
                'file_url': f"{settings.MINIO_ENDPOINT}/{settings.MINIO_BUCKET_NAME}/{file_name}"
            }, status=status.HTTP_200_OK)

        except Exception:
            return Response({'error': str(Exception)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# Проверяем celery

class ConversionTaskCreateView(generics.CreateAPIView):
    queryset = ConversionTask.objects.all()
    serializer_class = ConversionTaskSerializer

    def create(self, request, *args, **kwargs):
        file_url = request.data.get("file_url")
        # Создаем запись задачи
        task = ConversionTask.objects.create(
            task_id=str(uuid.uuid4()),
            input_file=file_url,
        )

        # Запускаем Celery задачу
        process_file_task.delay(task.task_id)

        serializer = self.get_serializer(task)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ConversionTaskDetailView(generics.RetrieveAPIView):
    queryset = ConversionTask.objects.all()
    serializer_class = ConversionTaskSerializer
    lookup_field = 'task_id'
