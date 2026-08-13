from django import forms

from accounts.models import CustomUser
from services.models import Service

from .models import Booking, BookingMessage


class BookingCreateForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            'customer',
            'service',
            'worker',
            'booking_date',
            'booking_time',
            'address',
            'problem_description',
        ]

    customer = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(role='customer'),
        required=False,
        label='Customer'
    )
    service = forms.ModelChoiceField(
        queryset=Service.objects.all(),
        label='Service'
    )
    worker = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(role='worker', worker_status='APPROVED'),
        required=False,
        label='Preferred Worker (optional)'
    )
    booking_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Booking Date'
    )
    booking_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        label='Booking Time'
    )

    def __init__(self, *args, **kwargs):
        selected_service = kwargs.pop('selected_service', None)
        super().__init__(*args, **kwargs)

        if selected_service is not None:
            queryset = Service.objects.all()
            queryset = queryset | Service.objects.filter(pk=selected_service.pk)
            self.fields['service'].queryset = queryset.order_by('name')
            if not self.data.get('service'):
                self.initial['service'] = selected_service
        else:
            self.fields['service'].queryset = Service.objects.all().order_by('name')


class BookingUpdateForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            'worker',
            'booking_date',
            'booking_time',
            'address',
            'problem_description',
        ]

    worker = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(role='worker', worker_status='APPROVED'),
        required=False,
        label='Preferred Worker (optional)'
    )


class BookingAssignForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['worker']

    worker = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(role='worker', worker_status='APPROVED'),
        required=False,
        label='Assign Verified Worker'
    )


class BookingMessageForm(forms.ModelForm):
    class Meta:
        model = BookingMessage
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Type your message...'})
        }


class BookingStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['status']


# ===== PHASE 2 FORMS: ServiceRequest, JobApplication, Job =====

class ServiceRequestCreateForm(forms.ModelForm):
    """Form for customers to create a service request"""
    class Meta:
        model_name = 'ServiceRequest'  # Placeholder - will be ServiceRequest once imported
        fields = [
            'title',
            'description',
            'location',
            'address',
            'preferred_date',
            'preferred_time_start',
            'preferred_time_end',
            'budget_min',
            'budget_max',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'What service do you need?',
                'maxlength': '200'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 5,
                'placeholder': 'Describe the problem, requirements, or details about your request...'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'City or area'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': 'Full address or location details'
            }),
            'preferred_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-input'
            }),
            'preferred_time_start': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-input'
            }),
            'preferred_time_end': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-input'
            }),
            'budget_min': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Minimum budget (optional)',
                'min': '0',
                'step': '0.01'
            }),
            'budget_max': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Maximum budget (optional)',
                'min': '0',
                'step': '0.01'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.service = kwargs.pop('service', None)
        super().__init__(*args, **kwargs)
        # Will be used to pre-fill service in view

    def clean(self):
        cleaned_data = super().clean()
        budget_min = cleaned_data.get('budget_min')
        budget_max = cleaned_data.get('budget_max')
        
        if budget_min and budget_max and budget_min > budget_max:
            raise forms.ValidationError("Minimum budget cannot be greater than maximum budget.")
        
        return cleaned_data


class JobApplicationForm(forms.ModelForm):
    """Form for workers to apply for a service request"""
    class Meta:
        model_name = 'JobApplication'  # Placeholder
        fields = [
            'proposed_price',
            'estimated_duration',
            'proposal_message',
            'can_start_date',
        ]
        widgets = {
            'proposed_price': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Your proposed price',
                'min': '0',
                'step': '0.01'
            }),
            'estimated_duration': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., 2 hours or 1 day 3 hours',
                'title': 'Format: HH:MM or use the pattern like 1 14:30 for 1 day and 14 hours 30 minutes'
            }),
            'proposal_message': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 6,
                'placeholder': 'Why are you the best choice for this job? Highlight your experience, skills, and approach to the work.'
            }),
            'can_start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-input'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        proposed_price = cleaned_data.get('proposed_price')
        
        if proposed_price and proposed_price <= 0:
            raise forms.ValidationError("Proposed price must be greater than 0.")
        
        return cleaned_data


class JobApplicationReviewForm(forms.ModelForm):
    """Form for customers to accept/reject job applications"""
    class Meta:
        model_name = 'JobApplication'  # Placeholder
        fields = ['status']
        widgets = {
            'status': forms.RadioSelect(choices=[
                ('ACCEPTED', '✓ Accept this application'),
                ('REJECTED', '✗ Reject this application'),
            ])
        }


class JobForm(forms.ModelForm):
    """Form for viewing/updating job details"""
    class Meta:
        model_name = 'Job'  # Placeholder
        fields = [
            'status',
            'scheduled_date',
            'scheduled_time_start',
            'scheduled_time_end',
            'actual_price',
        ]
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'scheduled_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-input'
            }),
            'scheduled_time_start': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-input'
            }),
            'scheduled_time_end': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-input'
            }),
            'actual_price': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Leave blank to use proposed price',
                'min': '0',
                'step': '0.01'
            }),
        }


class JobCompletionForm(forms.ModelForm):
    """Form for workers to mark job as completed"""
    class Meta:
        model_name = 'Job'  # Placeholder
        fields = ['actual_price', 'completion_notes', 'status']
        widgets = {
            'actual_price': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Final price (if different from proposed)',
                'min': '0',
                'step': '0.01'
            }),
            'completion_notes': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'What was completed? Any notes for the customer?'
            }),
            'status': forms.HiddenInput(),  # Auto-set to COMPLETED
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Status is auto-filled by view
        if self.instance:
            self.fields['status'].initial = 'COMPLETED'
