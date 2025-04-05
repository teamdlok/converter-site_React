import ffmpeg
from celery import shared_task

from converter_site_React import settings
from utils.minio_client import get_minio_client
from .models import ConversionTask
import time



@shared_task(bind=True)
def process_file_task(self, task_id, input_file_url):
    task = ConversionTask.objects.get(task_id=task_id )
    try:
        # Обновляем статус
        task.status = 'PROCESSING'
        task.save()

        in_filename = f"http://{input_file_url}"
        out_filename = f"{settings.MEDIA_ROOT}/uploads/video.mp3"

        stream = ffmpeg.input(in_filename)
        stream = ffmpeg.output(stream, out_filename)
        ffmpeg.run(stream, overwrite_output=True)

        minio_client = get_minio_client()
        output_filename = str(out_filename.split("/")[-1])
        minio_client.fput_object(settings.MINIO_BUCKET_NAME, output_filename, out_filename)
        print("Successfuly uploaded")

        task.result_file = f"{settings.MINIO_ENDPOINT}/{settings.MINIO_BUCKET_NAME}/{output_filename}"
        task.status = 'COMPLETED'
        task.save()

        return f"File {task.input_file} processed successfully"
    except Exception as e:
        print(f"!!! ERROR: {str(e)}")  # Логирование в консоль
        task.status = 'FAILED'
        task.save()
        raise self.retry(exc=e, countdown=60, max_retries=3)