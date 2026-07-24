from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    PasswordChangeForm
)
from services.models import Service
from .models import CustomUser


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(required=False, max_length=15, label='Phone number')
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 2}),
        label='Address'
    )
    preferred_contact_method = forms.ChoiceField(
        choices=CustomUser._meta.get_field('preferred_contact_method').choices,
        required=False,
        initial='Email',
        label='Preferred contact method'
    )
    receive_notifications = forms.BooleanField(required=False, initial=True, label='Receive notifications')

    role = forms.ChoiceField(
        choices=[('customer', 'Customer'), ('worker', 'Worker')],
        initial='customer',
        label='Register as'
    )
    register_as_worker = forms.BooleanField(required=False, widget=forms.HiddenInput(), label='Register as a worker')
    worker_service = forms.ModelChoiceField(
        queryset=Service.objects.all(),
        required=False,
        label='Service offered'
    )
    worker_service_category = forms.CharField(required=False, max_length=50, label='Service category')
    worker_skills = forms.CharField(required=False, max_length=200, label='Skills')
    worker_experience = forms.CharField(required=False, max_length=100, label='Experience')
    worker_service_area = forms.CharField(required=False, max_length=150, label='Service area')
    worker_portfolio_link = forms.URLField(required=False, label='Portfolio link')
    worker_hourly_rate = forms.DecimalField(required=False, max_digits=8, decimal_places=2, label='Hourly rate')
    worker_bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        label='Short bio'
    )

    class Meta:
        model = CustomUser
        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
            'phone',
            'address',
            'profile_picture',
            'preferred_contact_method',
            'receive_notifications',
            'password1',
            'password2',
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        selected_role = self.cleaned_data.get('role') or ('worker' if self.cleaned_data.get('register_as_worker') else 'customer')
        register_as_worker = selected_role == 'worker'
        user.role = selected_role
        user.preferred_contact_method = self.cleaned_data.get('preferred_contact_method') or 'Email'
        user.receive_notifications = self.cleaned_data.get('receive_notifications', True)
        user.is_verified_worker = False
        user.is_staff = False
        user.is_superuser = False
        if commit:
            user.save()

        if register_as_worker:
            from workers.models import WorkerProfile
            selected_service = self.cleaned_data.get('worker_service')
            WorkerProfile.objects.get_or_create(
                user=user,
                defaults={
                    'service': selected_service,
                    'service_category': (
                        selected_service.category if selected_service else self.cleaned_data.get('worker_service_category')
                    ) or 'General',
                    'skills': self.cleaned_data.get('worker_skills') or 'General services',
                    'experience': self.cleaned_data.get('worker_experience') or 'New',
                    'service_area': self.cleaned_data.get('worker_service_area') or 'Local',
                    'portfolio_link': self.cleaned_data.get('worker_portfolio_link'),
                    'hourly_rate': self.cleaned_data.get('worker_hourly_rate'),
                    'bio': self.cleaned_data.get('worker_bio'),
                }
            )
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone',
            'address',
            'profile_picture',
            'preferred_contact_method',
            'receive_notifications',
        ]


class CustomPasswordChangeForm(PasswordChangeForm):
    pass