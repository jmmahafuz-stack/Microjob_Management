from django import forms

from services.models import Service, Category
from .models import WorkerProfile


class WorkerProfileForm(forms.ModelForm):
    service = forms.ModelChoiceField(
        queryset=Service.objects.all(),
        required=False,
        label='Service offered'
    )
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Categories you work in'
    )

    class Meta:
        model = WorkerProfile
        fields = [
            'categories',
            'service',
            'service_category',
            'skills',
            'experience_years',
            'service_area',
            'languages',
            'bio',
            'portfolio_link',
            'id_verification_document',
            'hourly_rate',
            'response_time',
            'payout_status',
            'training_status',
            'verification_status',
        ]


class WorkerVerificationForm(forms.ModelForm):
    service = forms.ModelChoiceField(
        queryset=Service.objects.all(),
        required=False,
        label='Service offered'
    )
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Categories you work in'
    )

    class Meta:
        model = WorkerProfile
        fields = [
            'categories',
            'service',
            'service_category',
            'skills',
            'experience_years',
            'service_area',
            'languages',
            'bio',
            'portfolio_link',
            'hourly_rate',
            'response_time',
            'payout_status',
            'training_status',
            'verification_status',
        ]
