import io
from celery import shared_task
from django.core.mail import EmailMessage
from django.conf import settings
from openpyxl import Workbook
from .models import Employee


@shared_task
def send_employee_backup():
    # 1. Создаем Excel файл в памяти
    wb = Workbook()
    ws = wb.active
    ws.title = "Employees Backup"

    # Заголовки
    headers = ['ID', 'Фамилия', 'Имя', 'Отчество', 'Филиал', 'Город', 'Email', 'Личный тел.', 'Раб. тел.']
    ws.append(headers)

    # Данные
    for emp in Employee.objects.all():
        ws.append([
            emp.id, emp.last_name, emp.first_name, emp.middle_name,
            emp.branch, emp.city, emp.email, emp.personal_phone, emp.work_phone
        ])

    # Сохраняем в байтовый поток
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    # 2. Формируем письмо
    email = EmailMessage(
        subject='Плановый бэкап базы сотрудников',
        body='Во вложении актуальный список сотрудников компании на текущую дату.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.ARCHIVE_EMAIL],
    )

    # Прикрепляем файл
    email.attach('backup_employees.xlsx', output.read(),
                 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    # 3. Отправляем
    email.send()
    return "Backup sent successfully"
