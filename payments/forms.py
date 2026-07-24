from django import forms

from .models import Payment


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = [
            'amount',
            'payment_method',
            'transaction_id',
            'payment_status',
            'receipt',
        ]


class CustomerPaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = [
            'payment_method',
            'transaction_id',
            'receipt',
        ]
        widgets = {
            'transaction_id': forms.TextInput(attrs={'placeholder': 'Enter transaction ID when payment is complete'}),
        }
