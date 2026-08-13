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
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'transaction_id': forms.TextInput(attrs={
                'placeholder': 'Enter transaction ID or reference number',
                'class': 'form-control'
            }),
            'receipt': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        transaction_id = cleaned_data.get('transaction_id')
        receipt = cleaned_data.get('receipt')

        if not transaction_id and not receipt:
            raise forms.ValidationError(
                'Please enter a transaction ID or upload a payment receipt to confirm the payment.'
            )

        return cleaned_data
