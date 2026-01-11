from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

phone_validator = RegexValidator(
    regex=r'^[0-9+\(\)\-\s]+$',
    message="Номер телефона может содержать только цифры и символы: +, (, ), -, пробел."
)


class Employee(models.Model):
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    middle_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Отчество")
    position = models.CharField(max_length=150, verbose_name="Должность", default="Сотрудник")
    branch = models.CharField(max_length=200, verbose_name="Филиал")
    city = models.CharField(max_length=100, verbose_name="Город")
    email = models.EmailField(unique=True, verbose_name="Почта (рабочая)")
    personal_phone = models.CharField(
        max_length=20, blank=True, null=True,
        validators=[phone_validator], verbose_name="Номер телефона (личный)"
    )
    work_phone = models.CharField(
        max_length=20, blank=True, null=True,
        validators=[phone_validator], verbose_name="Номер телефона (рабочий)"
    )

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
        ordering = ['last_name']

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    def clean(self):
        super().clean()
        if not self.personal_phone and not self.work_phone:
            raise ValidationError("Заполните хотя бы один номер телефона.")


class CorrectionProposal(models.Model):
    STATUS_CHOICES = [
        ('pending', 'На рассмотрении'),
        ('approved', 'Принято'),
        ('rejected', 'Отклонено'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Сотрудник")
    # Здесь хранится техническое имя поля (например, 'city')
    field_name = models.CharField(max_length=100, verbose_name="Имя поля")
    new_value = models.TextField(verbose_name="Новое значение")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")

    def save(self, *args, **kwargs):
        if self.pk:
            # Получаем текущее состояние заявки из базы данных
            old_instance = CorrectionProposal.objects.get(pk=self.pk)

            # ЗАПРЕТ: Если статус уже был "Принято" или "Отклонено", выдаем ошибку
            if old_instance.status in ['approved', 'rejected']:
                raise ValidationError(
                    f"Нельзя изменить заявку со статусом '{old_instance.get_status_display()}'"
                )

            # Логика применения изменений (выполняется только если статус меняется на approved)
            if old_instance.status == 'pending' and self.status == 'approved':
                attr_name = self.field_name.strip().lower()
                if hasattr(self.employee, attr_name):
                    setattr(self.employee, attr_name, self.new_value)
                    self.employee.full_clean()
                    self.employee.save()

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Предложение"
        verbose_name_plural = "Предложения"
