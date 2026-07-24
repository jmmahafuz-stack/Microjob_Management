from django import forms
from .models import Service


class ServiceForm(forms.ModelForm):

    class Meta:
        model = Service
        fields = '__all__'