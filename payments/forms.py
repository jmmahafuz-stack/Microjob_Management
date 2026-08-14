from django import forms

from .models import Payment


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = [
            'customer_amount',
            'payment_method',
            'transaction_id',
            'payment_status',
            'receipt',
        ]


class CustomerPaymentForm(forms.ModelForm):
    confirm_payment = forms.BooleanField(
        required=False,
        label='I have completed the payment and want to confirm it now.',
    )

    class Meta:
        model = Payment
        fields = [
            'payment_method',
            'transaction_id',
            'receipt',
            'confirm_payment',
        ]

        widgets = {
            'payment_method': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'transaction_id': forms.TextInput(
                attrs={
                    'placeholder': 'Optional transaction reference',
                    'class': 'form-control'
                }
            ),
            'receipt': forms.ClearableFileInput(
                attrs={'class': 'form-control'}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        transaction_id = cleaned_data.get('transaction_id')
        receipt = cleaned_data.get('receipt')
        confirm_payment = cleaned_data.get('confirm_payment')

        if not transaction_id and not receipt and not confirm_payment:
            raise forms.ValidationError(
                'Please confirm the payment and provide a transaction ID or receipt.'
            )

        return cleaned_data