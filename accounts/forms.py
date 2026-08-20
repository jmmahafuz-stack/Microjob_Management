import re

from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    PasswordChangeForm
)
from services.models import Category
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
    worker_categories = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        required=False,
        empty_label='Select your main work category',
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Work Category',
        help_text='Select the main category/profession you work in'
    )
    worker_skills = forms.CharField(required=False, max_length=200, label='Skills')
    worker_experience = forms.CharField(
        required=False,
        max_length=100,
        label='Experience',
        widget=forms.NumberInput(attrs={'min': '0', 'step': '1', 'placeholder': 'Years'})
    )
    worker_service_area = forms.CharField(required=False, max_length=150, label='Service area')
    worker_nid_number = forms.CharField(
        required=False,
        max_length=30,
        label='NID Number',
        widget=forms.TextInput(attrs={'placeholder': 'National ID number'})
    )
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set querysets dynamically to get latest data
        self.fields['worker_categories'].queryset = Category.objects.filter(is_active=True)

    def clean_role(self):
        value = self.cleaned_data.get('role')
        if value not in {'customer', 'worker', 'admin'}:
            return 'customer'
        return value

    def clean_worker_experience(self):
        value = self.cleaned_data.get('worker_experience')
        if not value:
            return 0

        match = re.search(r'(\d+)', str(value))
        if match:
            return int(match.group(1))

        return 0

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        if role == 'worker' and not cleaned_data.get('worker_categories'):
            self.add_error('worker_categories', 'Please select your main work category.')
        return cleaned_data

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
                selected_category = self.cleaned_data.get('worker_categories')
                # Worker registration no longer requires a specific service, text category,
                # or hourly rate. Workers can manage those details later from their profile.
                profile.service = None
                profile.service_category = ''
                if selected_category:
                    profile.profession = selected_category.name
                profile.skills = self.cleaned_data.get('worker_skills') or profile.skills
                profile.experience_years = self.clean_worker_experience()
                profile.service_area = self.cleaned_data.get('worker_service_area') or profile.service_area
                profile.nid_number = self.cleaned_data.get('worker_nid_number') or profile.nid_number
                profile.bio = self.cleaned_data.get('worker_bio') or profile.bio
                profile.verification_status = 'Pending'
                profile.training_status = 'Pending'
                profile.save()
                
                # Add selected category
                if selected_category:
                    profile.categories.set([selected_category])

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