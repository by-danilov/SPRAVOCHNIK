import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('SPRAVOCHNIK')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматический поиск задач в приложениях (tasks.py)
app.autodiscover_tasks()

# Настройка расписания: 1 и 15 число каждого месяца в 00:00
app.conf.beat_schedule = {
    'backup-every-1st-and-15th': {
        'task': 'core.tasks.send_employee_backup',
        'schedule': crontab(0, 0, day_of_month='1,15'),
    },
}
