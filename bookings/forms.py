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
        queryset=Service.objects.filter(is_available=True),
        label='Service'
    )
    worker = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(role='worker', is_verified_worker=True),
        required=False,
        label='Preferred Worker (optional)'
    )


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
        queryset=CustomUser.objects.filter(role='worker', is_verified_worker=True),
        required=False,
        label='Preferred Worker (optional)'
    )


class BookingAssignForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['worker']

    worker = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(role='worker', is_verified_worker=True),
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
