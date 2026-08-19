from django import forms
from .models import Service, Category


class ServiceForm(forms.ModelForm):
    """Form for creating and editing services"""
    
    class Meta:
        model = Service
        fields = ['name', 'category', 'description', 'price', 'image', 'duration', 'location', 'featured', 'is_available']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Service Name'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Detailed description of the service'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price', 'step': '0.01'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 2 hours'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Service location (optional)'}),
            'featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        
        if price and price <= 0:
            raise forms.ValidationError('Price must be greater than 0.')
        
        return cleaned_data


class CategoryForm(forms.ModelForm):
    """Form for creating and editing service categories"""
    
    class Meta:
        model = Category
        fields = ['name', 'description', 'icon', 'image', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Category description'}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Icon or emoji (e.g., 🔧)'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }