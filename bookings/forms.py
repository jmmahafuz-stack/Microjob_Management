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
