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
        required=True,
        label='I have completed the payment and want to submit it for verification.',
    )
    receipt = forms.ImageField(
        required=False,
        label='Payment proof image (optional)',
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
        }),
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
                    'placeholder': 'Enter your transaction number',
                    'class': 'form-control'
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        if not cleaned_data.get('transaction_id'):
            raise forms.ValidationError(
                'Please enter the transaction number for this payment.'
            )

        return cleaned_data