from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    PasswordChangeForm
)
from services.models import Service
from workers.models import WorkerProfile
from .models import CustomUser


class RegisterForm(UserCreationForm):
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'type': 'password',
            'autocomplete': 'new-password'
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'type': 'password',
            'autocomplete': 'new-password'
        })
    )
    
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
        required=False,
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

    def clean_role(self):
        value = self.cleaned_data.get('role')
        if value not in {'customer', 'worker', 'admin'}:
            return 'customer'
        return value

    def save(self, commit=True):
        user = super().save(commit=False)
        selected_role = self.cleaned_data.get('role') or 'customer'
        user.role = selected_role if selected_role in {'customer', 'worker', 'admin'} else 'customer'
        user.preferred_contact_method = self.cleaned_data.get('preferred_contact_method') or 'Email'
        user.receive_notifications = self.cleaned_data.get('receive_notifications', True)
        user.is_staff = False
        user.is_superuser = False
        
        # Set status based on role
        if user.role == 'worker':
            user.worker_status = 'PENDING'
            user.customer_status = None
        else:  # customer or other
            user.customer_status = 'ACTIVE'
            user.worker_status = None
        
        if commit:
            user.save()

            if user.role == 'worker':
                profile, _ = WorkerProfile.objects.get_or_create(user=user)
                service = self.cleaned_data.get('worker_service')
                profile.service = service
                profile.service_category = self.cleaned_data.get('worker_service_category') or (service.category if service else '')
                profile.skills = self.cleaned_data.get('worker_skills') or profile.skills
                profile.experience_years = int(self.cleaned_data.get('worker_experience') or 0) if self.cleaned_data.get('worker_experience') else 0
                profile.service_area = self.cleaned_data.get('worker_service_area') or profile.service_area
                profile.portfolio_link = self.cleaned_data.get('worker_portfolio_link') or profile.portfolio_link
                profile.hourly_rate = self.cleaned_data.get('worker_hourly_rate') or profile.hourly_rate
                profile.bio = self.cleaned_data.get('worker_bio') or profile.bio
                profile.verification_status = 'Pending'
                profile.training_status = 'Pending'
                profile.save()

        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "facebook-input",
            "placeholder": "Email or username",
            "autocomplete": "username",
        }),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "facebook-input",
            "placeholder": "Password",
            "autocomplete": "current-password",
        }),
    )


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