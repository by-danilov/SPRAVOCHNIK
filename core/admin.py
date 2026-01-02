from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Employee, CorrectionProposal


# Настройка для импорта/экспорта сотрудников
class EmployeeResource(resources.ModelResource):
    class Meta:
        model = Employee
        import_id_fields = ['id']  # Позволяет обновлять существующих по ID


@admin.register(Employee)
class EmployeeAdmin(ImportExportModelAdmin):
    resource_class = EmployeeResource
    list_display = ('last_name', 'first_name', 'branch', 'city', 'email', 'work_phone')
    search_fields = ('last_name', 'city', 'branch', 'email')
    list_filter = ('branch', 'city')


@admin.register(CorrectionProposal)
class CorrectionProposalAdmin(admin.ModelAdmin):
    # Добавляем колонку "Было", чтобы админ видел разницу сразу
    list_display = ('employee', 'field_name', 'get_current_val', 'new_value', 'status', 'created_at')
    list_filter = ('status', 'field_name')
    # Добавляем наши действия
    actions = ['approve_selected_proposals', 'reject_selected_proposals']

    def get_current_val(self, obj):
        """Отображает текущее значение поля в базе данных"""
        try:
            return getattr(obj.employee, obj.field_name)
        except:
            return "Ошибка поля"

    get_current_val.short_description = "Текущее значение"

    def approve_selected_proposals(self, request, queryset):
        """Действие для массового одобрения"""
        count = 0
        for proposal in queryset:
            if proposal.status != 'approved':
                proposal.status = 'approved'
                # ВАЖНО: вызываем сохранение каждого объекта вручную,
                # чтобы сработал метод save() из models.py
                proposal.save()
                count += 1
        self.message_user(request, f"Успешно одобрено и применено {count} предложений.")

    approve_selected_proposals.short_description = "✅ Принять выбранные обновления"

    def reject_selected_proposals(self, request, queryset):
        """Действие для массового отклонения"""
        updated = queryset.update(status='rejected')
        self.message_user(request, f"{updated} предложений были отклонены.")

    reject_selected_proposals.short_description = "❌ Отклонить выбранные обновления"
