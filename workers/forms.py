from django import forms

from services.models import Service, Category
from .models import WorkerProfile


class WorkerProfileForm(forms.ModelForm):
    """Form for workers to update profile details without changing category."""
    
    service = forms.ModelChoiceField(
        queryset=Service.objects.none(),
        required=False,
        label='Service offered'
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Tell customers about yourself'}),
        label='Short bio'
    )
    hourly_rate = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Hourly rate (optional)'}),
        label='Hourly rate'
    )

    class Meta:
        model = WorkerProfile
        fields = [
            'profession',
            'service',
            'skills',
            'experience_years',
            'service_area',
            'languages',
            'bio',
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
            'id_verification_document': forms.FileInput(attrs={'class': 'form-control'}),
            'response_time': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set querysets dynamically to get latest data
        profile = self.instance
        self.fields['service'].queryset = Service.objects.filter(
            category__in=profile.categories.all()
        ) if profile.pk else Service.objects.none()
    
    def clean(self):
        cleaned_data = super().clean()
        profession = cleaned_data.get('profession')
        if not profession or not profession.strip():
            raise forms.ValidationError('Profession is required.')
        
        return cleaned_data


class WorkerVerificationForm(forms.ModelForm):
    """Form for admin to verify/approve workers"""
    
    service = forms.ModelChoiceField(
        queryset=Service.objects.none(),
        required=False,
        label='Service offered'
    )
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Categories they work in'
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Tell customers about yourself'}),
        label='Short bio'
    )
    hourly_rate = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Hourly rate (optional)'}),
        label='Hourly rate'
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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set querysets dynamically to get latest data
        self.fields['service'].queryset = Service.objects.all()
        self.fields['categories'].queryset = Category.objects.filter(is_active=True)

    def clean_categories(self):
        categories = self.cleaned_data['categories']
        if categories.count() != 1:
            raise forms.ValidationError('Assign exactly one category to each worker.')
        return categories
