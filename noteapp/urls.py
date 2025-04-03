from django.urls import path
from .import views
from .views import FileUploadView, GeneratePresignedURL
from .views import ConversionTaskCreateView, ConversionTaskDetailView

urlpatterns = [
    path("notes/", views.notes, name="notes"),
    path("notes/<slug:slug>", views.note_detail, name="note_detail"),
    path("notes-search/", views.search_notes, name='notes-search'),
    path("upload/", FileUploadView.as_view(), name='file-upload'),
    path("generate-presigned-url/", GeneratePresignedURL.as_view(), name="generate-presigned-url"),
    path('tasks/', ConversionTaskCreateView.as_view(), name='create-task'),
    path('tasks/<str:task_id>/', ConversionTaskDetailView.as_view(), name='task-detail'),
]

# # endpoints:
# GET_ALL_NOTES_and_CREATE_NEW_NOTE = "127.0.0.1:8000/api/notes"
# GET_SPECIFIC_NOTE = "http://127.0.0.1:8000/api/notes/note-slug"
# GET_SEARCH = "http://127.0.0.1:8000/api/notes-search/?search="
# POST_FILE = "http://127.0.0.1:8000/api/upload/"
# POST_GENERATE_MINIO_URL = "http://127.0.0.1:8000/api/generate-presigned-url/"