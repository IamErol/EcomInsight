import os
from celery import shared_task
from django.conf.global_settings import MEDIA_ROOT
from django.contrib.auth import get_user_model
from .import_export import write_to_csv


@shared_task
def generate_csv_task(user_id):
    """Celery task for generating CSV file."""
    user = get_user_model().objects.get(id=user_id)
    file_path = os.path.join(MEDIA_ROOT, f'products_{user_id}.csv')
    write_to_csv(user, file_path)
    return file_path
