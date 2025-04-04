import ffmpeg
from celery import shared_task

from converter_site_React import settings
from utils.minio_client import get_minio_client
from .models import ConversionTask
import time



@shared_task(bind=True)
def process_file_task(self, task_id):
    task = ConversionTask.objects.get(task_id=task_id)
    try:
        # Обновляем статус
        task.status = 'PROCESSING'
        task.save()

        in_filename = "http://176.222.54.127:9001/api/v1/download-shared-object/aHR0cDovLzEyNy4wLjAuMTo5MDAwL2ZpbGUtc3RvcmFnZS8lRDAlOUElRDAlQjAlRDAlQkQlRDElODYlRDAlQkIlRDAlQjUlRDElODAlMjAlRDAlOTMlRDAlQjglMjAtJTIwJUQwJUEyJUQwJUI1JUQwJUJEJUQxJThDJTIwJUQwJUJEJUQwJUIwJTIwJUQwJUExJUQxJTgyJUQwJUI1JUQwJUJEJUQwJUI1JTI4MiUyOS5tcDQ_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1VRVBDQUhHVlpHWFpTT005ODMzQiUyRjIwMjUwNDA0JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDQwNFQwNDAxMjRaJlgtQW16LUV4cGlyZXM9NDMyMDAmWC1BbXotU2VjdXJpdHktVG9rZW49ZXlKaGJHY2lPaUpJVXpVeE1pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SmhZMk5sYzNOTFpYa2lPaUpWUlZCRFFVaEhWbHBIV0ZwVFQwMDVPRE16UWlJc0ltVjRjQ0k2TVRjME16YzRNakl4TlN3aWNHRnlaVzUwSWpvaWRHVmhiV1JzYjJzaWZRLlN1SUdjRVBEOEpieG5Tc0RPTGlrUWJwRkhJbktzdG9XeklfUzVhb2dFMTYxa1RncVNhWVFrbDFNNzVsOW1PTl8tN3MzTklnRmhaUHNtVm9fc1RHcEhRJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZ2ZXJzaW9uSWQ9bnVsbCZYLUFtei1TaWduYXR1cmU9YTRlY2FmYTg2ZTFlNWNjZDEzZGNlYmI3ZTQ4NDFlNjIwN2FmZmZiMDljNmQ0YWQ3Mzk4OWVhNjZmNDQwOGE0Ng"
        out_filename = f"{settings.MEDIA_ROOT}/uploads/video.mp3"

        stream = ffmpeg.input(in_filename)
        stream = ffmpeg.output(stream, out_filename)
        ffmpeg.run(stream)

        minio_client = get_minio_client()
        minio_client.fput_object(settings.MINIO_BUCKET_NAME, "file_uploaded.webp", out_filename)
        print("Successfuly uploaded")

        task.result_file = f"processed_file"
        task.status = 'COMPLETED'
        task.save()

        return f"File {task.input_file} processed successfully"
    except Exception as e:
        print(f"!!! ERROR: {str(e)}")  # Логирование в консоль
        task.status = 'FAILED'
        task.save()
        raise self.retry(exc=e, countdown=60, max_retries=3)