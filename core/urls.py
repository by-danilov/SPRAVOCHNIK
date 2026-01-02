from django.urls import path
from .views import EmployeeListView, CorrectionProposalCreateView

urlpatterns = [
    path('', EmployeeListView.as_view(), name='employee_list'),
    path('propose/<int:employee_id>/', CorrectionProposalCreateView.as_view(), name='propose_correction'),
]
