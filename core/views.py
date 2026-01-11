from django.views.generic import ListView, CreateView
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Employee, CorrectionProposal
from .forms import CorrectionProposalForm

class EmployeeListView(ListView):
    model = Employee
    template_name = 'core/employee_list.html'
    context_object_name = 'employees'
    paginate_by = 10

    def get_queryset(self):
        q = self.request.GET.get('search', '')
        object_list = Employee.objects.all()
        if q:
            object_list = object_list.filter(
                Q(last_name__icontains=q) |
                Q(first_name__icontains=q) |
                Q(position__icontains=q) |
                Q(branch__icontains=q) |
                Q(city__icontains=q) |
                Q(email__icontains=q)
            )
        return object_list

class CorrectionProposalCreateView(CreateView):
    model = CorrectionProposal
    form_class = CorrectionProposalForm
    template_name = 'core/proposal_form.html'
    success_url = reverse_lazy('employee_list')

    def form_valid(self, form):
        form.instance.employee = get_object_or_404(Employee, id=self.kwargs['employee_id'])
        messages.success(self.request, "Предложение отправлено!")
        return super().form_valid(form)
