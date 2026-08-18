from django import forms

from services.models import Service, Category
from .models import WorkerProfile


class WorkerProfileForm(forms.ModelForm):
    """Form for workers to update their profile"""
    
    service = forms.ModelChoiceField(
        queryset=Service.objects.all(),
        required=False,
        label='Service offered'
    )
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=True,
        widget=forms.CheckboxSelectMultiple,
        label='Categories you work in (Select at least one)',
        help_text='Select all the categories/professions you can work with'
    )

    class Meta:
        model = WorkerProfile
        fields = [
            'profession',
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
        ]
        widgets = {
            'profession': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Electrician'}),
            'skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Comma-separated skills'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'service_area': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Area of service'}),
            'languages': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Languages you speak'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Tell customers about yourself'}),
            'portfolio_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Link to your portfolio'}),
            'id_verification_document': forms.FileInput(attrs={'class': 'form-control'}),
            'hourly_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Hourly rate (optional)'}),
            'response_time': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        profession = cleaned_data.get('profession')
        categories = cleaned_data.get('categories')
        
        if not profession or not profession.strip():
            raise forms.ValidationError('Profession is required.')
        
        if not categories:
            raise forms.ValidationError('Please select at least one category.')
        
        return cleaned_data


class WorkerVerificationForm(forms.ModelForm):
    """Form for admin to verify/approve workers"""
    
    service = forms.ModelChoiceField(
        queryset=Service.objects.all(),
        required=False,
        label='Service offered'
    )
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Categories they work in'
    )

    class Meta:
        model = WorkerProfile
        fields = [
            'profession',
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
            'verification_status',
            'training_status',
        ]
        widgets = {
            'profession': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'verification_status': forms.Select(attrs={'class': 'form-control'}),
            'training_status': forms.Select(attrs={'class': 'form-control'}),
        }
