from celery import shared_task
from .models import ConversionTask
import time



@shared_task(bind=True)
def process_file_task(self, task_id):
    task = ConversionTask.objects.get(task_id=task_id)
    try:
        # Обновляем статус
        task.status = 'PROCESSING'
        task.save()

        # Имитация долгой обработки файла
        time.sleep(10)

        # "Результат" обработки
        task.result_file = f"processed_{task.input_file}"
        task.status = 'COMPLETED'
        task.save()

        return f"File {task.input_file} processed successfully"
    except Exception as e:
        task.status = 'FAILED'
        task.save()
        raise self.retry(exc=e, countdown=60, max_retries=3)

