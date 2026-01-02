from django import forms
from .models import CorrectionProposal


class CorrectionProposalForm(forms.ModelForm):
    FIELD_CHOICES = [
        ('last_name', 'Фамилия'),
        ('first_name', 'Имя'),
        ('middle_name', 'Отчество'),
        ('branch', 'Филиал'),
        ('city', 'Город'),
        ('email', 'Email'),
        ('personal_phone', 'Личный телефон'),
        ('work_phone', 'Рабочий телефон'),
    ]

    field_name = forms.ChoiceField(
        choices=FIELD_CHOICES,
        label="Какое поле содержит ошибку?",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    new_value = forms.CharField(
        label="Корректные данные",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите правильное значение'})
    )

    class Meta:
        model = CorrectionProposal
        fields = ['field_name', 'new_value']
