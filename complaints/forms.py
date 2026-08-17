from django import forms

from .models import Complaint


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['subject', 'description']


class ComplaintReplyForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['reply', 'status']
