from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Employee, CorrectionProposal


# Настройка для импорта/экспорта сотрудников
class EmployeeResource(resources.ModelResource):
    class Meta:
        model = Employee
        fields = ('id', 'last_name', 'first_name', 'position', 'branch', 'city', 'email', 'personal_phone',
                  'work_phone')
        import_id_fields = ['id']  # Позволяет обновлять существующих по ID


@admin.register(Employee)
class EmployeeAdmin(ImportExportModelAdmin):
    resource_class = EmployeeResource
    list_display = ('last_name', 'first_name', 'position', 'branch', 'city', 'email', 'work_phone')
    search_fields = ('last_name', 'city', 'position', 'branch', 'email')
    list_filter = ('branch', 'city', 'position')


@admin.register(CorrectionProposal)
class CorrectionProposalAdmin(admin.ModelAdmin):
    # list_display[2] теперь точно указывает на существующий метод get_current_val
    list_display = ('employee', 'field_name', 'get_current_val', 'new_value', 'status', 'created_at')
    list_filter = ('status', 'field_name')
    actions = ['approve_selected_proposals', 'reject_selected_proposals']

    # Метод для отображения текущего значения (информативно для админа)
    def get_current_val(self, obj):
        try:
            return getattr(obj.employee, obj.field_name)
        except Exception:
            return "—"

    get_current_val.short_description = "Текущее значение"

    # Блокировка полей, если заявка уже закрыта (approved/rejected)
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status in ['approved', 'rejected']:
            # Все поля становятся только для чтения
            return [f.name for f in self.model._meta.fields]
        return ['created_at']

    def approve_selected_proposals(self, request, queryset):
        success_count = 0
        skipped_count = 0

        # Добавляем сортировку .order_by('created_at'),
        # чтобы изменения шли по порядку
        proposals_to_approve = queryset.filter(status='pending').order_by('created_at')

        for proposal in proposals_to_approve:
            proposal.status = 'approved'
            # Вызов save() запустит логику с refresh_from_db() из модели
            proposal.save()
            success_count += 1

        # Вычисляем пропущенные (те, что не были в pending)
        skipped_count = queryset.count() - success_count

        if success_count:
            self.message_user(request, f"Успешно применено {success_count} предложений.")
        if skipped_count > 0:
            self.message_user(request, f"{skipped_count} заявок пропущено (уже обработаны).", level='warning')

    approve_selected_proposals.short_description = "✅ Принять выбранные"

    def reject_selected_proposals(self, request, queryset):
        count = queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f"Отклонено {count} заявок.")

    reject_selected_proposals.short_description = "❌ Отклонить выбранные"
