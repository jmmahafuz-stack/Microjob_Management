from datetime import timedelta

from django import forms
from django.db.models import Q
from accounts.models import CustomUser
from services.models import Service

from .models import Booking, BookingMessage, ServiceRequest, JobApplication, Job, WorkerResponse


class BookingCreateForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            'booking_date',
            'booking_time',
            'address',
            'problem_description',
            'problem_photo',
        ]

    booking_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Booking Date'
    )
    booking_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        label='Booking Time'
    )

    def __init__(self, *args, **kwargs):
        kwargs.pop('selected_service', None)
        kwargs.pop('selected_worker', None)
        super().__init__(*args, **kwargs)


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
        fields = ['message', 'attachment']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Type your message...'}),
            'attachment': forms.ClearableFileInput(attrs={
                'accept': 'image/*,.pdf',
            }),
        }


class BookingStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['status']


class WorkerResponseForm(forms.ModelForm):
    """Form for workers to respond to bookings"""
    class Meta:
        model = WorkerResponse
        fields = ['status', 'message']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-input',
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'Tell the customer about your response, availability, or questions...'
            })
        }


# ===== PHASE 2 FORMS: ServiceRequest, JobApplication, Job =====

class ServiceRequestCreateForm(forms.ModelForm):
    """Form for customers to create a service request"""
    class Meta:
        model = ServiceRequest
        fields = [
            'service',
            'title',
            'description',
            'problem_photo',
            'location',
            'address',
            'preferred_date',
            'preferred_time_start',
            'preferred_time_end',
            'budget_min',
            'budget_max',
        ]
        widgets = {
            'service': forms.Select(attrs={'class': 'form-select'}),
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
        if self.service:
            self.fields['service'].initial = self.service

    def clean(self):
        cleaned_data = super().clean()
        budget_min = cleaned_data.get('budget_min')
        budget_max = cleaned_data.get('budget_max')
        
        if budget_min and budget_max and budget_min > budget_max:
            raise forms.ValidationError("Minimum budget cannot be greater than maximum budget.")
        
        return cleaned_data


class JobApplicationForm(forms.ModelForm):
    """Form for workers to apply for a service request"""
    duration_hours = forms.ChoiceField(
        choices=[(str(value), str(value)) for value in range(1, 25)],
        label='Hours',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    duration_minutes = forms.ChoiceField(
        choices=[(str(value), f'{value:02d}') for value in range(0, 60, 15)],
        label='Minutes',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    agreed_to_schedule = forms.BooleanField(
        required=True,
        label="I agree to the customer's requested date and time"
    )
    proposal_message = forms.CharField(
        required=False,
        label='Proposal Message (optional)',
        widget=forms.Textarea(attrs={
            'class': 'form-textarea',
            'rows': 6,
            'placeholder': 'Add an optional message about your experience and approach.'
        })
    )

    class Meta:
        model = JobApplication
        fields = [
            'proposed_price',
            'proposal_message',
            'can_start_date',
            'agreed_to_schedule',
        ]
        widgets = {
            'proposed_price': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Your proposed price',
                'min': '0',
                'step': '0.01'
            }),
            'can_start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-input'
            }),
            'agreed_to_schedule': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.service_request = kwargs.pop('service_request', None)
        self.worker = kwargs.pop('worker', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        proposed_price = cleaned_data.get('proposed_price')
        hours = cleaned_data.get('duration_hours')
        minutes = cleaned_data.get('duration_minutes')

        if hours is not None and minutes is not None:
            cleaned_data['estimated_duration'] = timedelta(
                hours=int(hours), minutes=int(minutes)
            )
        
        if proposed_price and proposed_price <= 0:
            raise forms.ValidationError("Proposed price must be greater than 0.")

        if (
            cleaned_data.get('agreed_to_schedule')
            and self.service_request
            and cleaned_data.get('can_start_date') != self.service_request.preferred_date
        ):
            raise forms.ValidationError(
                "To agree to the customer's schedule, your start date must match the preferred date."
            )

        if self.service_request and cleaned_data.get('agreed_to_schedule'):
            scheduled_date = self.service_request.preferred_date
            requested_start = self.service_request.preferred_time_start
            requested_end = self.service_request.preferred_time_end
            worker = self.worker or self.instance.worker
            assigned_jobs = Job.objects.filter(
                worker=worker,
                scheduled_date=scheduled_date,
                status__in=['CONFIRMED', 'IN_PROGRESS'],
            ) if worker else Job.objects.none()

            for existing_job in assigned_jobs:
                existing_start = existing_job.scheduled_time_start
                existing_end = existing_job.scheduled_time_end
                has_overlap = False

                if requested_start and existing_start:
                    if requested_end and existing_end:
                        has_overlap = (
                            requested_start < existing_end
                            and requested_end > existing_start
                        )
                    elif requested_end:
                        has_overlap = requested_start < existing_job.get_estimated_end_time()
                    else:
                        has_overlap = requested_start < existing_job.get_estimated_end_time()
                elif not requested_start or not existing_start:
                    has_overlap = True

                if has_overlap:
                    existing_time = existing_start.strftime('%I:%M %p') if existing_start else 'unspecified time'
                    if existing_end:
                        existing_time += f" - {existing_end.strftime('%I:%M %p')}"
                    raise forms.ValidationError(
                        f"You are already assigned to another job at this time: "
                        f"{existing_job.title} on {existing_job.scheduled_date:%b %d, %Y} "
                        f"({existing_time}). Please choose a different job time."
                    )
        
        return cleaned_data

    def save(self, commit=True):
        application = super().save(commit=False)
        application.estimated_duration = self.cleaned_data['estimated_duration']
        if commit:
            application.save()
        return application


class JobApplicationReviewForm(forms.ModelForm):
    """Form for customers to accept/reject job applications"""
    class Meta:
        model = JobApplication
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
        model = Job
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
        model = Job
        fields = ['actual_price', 'completion_notes']
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
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Status is auto-set by view, not included in form


class JobPriceUpdateForm(forms.ModelForm):
    """Form for workers to update the price before completion."""
    class Meta:
        model = Job
        fields = ['actual_price']
        widgets = {
            'actual_price': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Leave blank to use proposed price',
                'min': '0.01',
                'step': '0.01',
            }),
        }

    def clean_actual_price(self):
        price = self.cleaned_data['actual_price']
        if price is not None and price <= 0:
            raise forms.ValidationError('Price must be greater than 0.')
        return price
