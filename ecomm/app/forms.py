from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    SetPasswordForm,
    PasswordResetForm,
    PasswordChangeForm,
    AuthenticationForm,
    UsernameField
)
from django.contrib.auth.models import User
from .models import Customer

class LoginForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(attrs={
        'autofocus': 'True',
        'class': 'form-control form-control-modern',
        'placeholder': 'Enter your username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'autocomplete': 'current-password',
        'class': 'form-control form-control-modern',
        'placeholder': 'Enter your password'
    }))

class CustomerRegistrationForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'autofocus': 'True',
        'class': 'form-control form-control-modern',
        'placeholder': 'Choose a username'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control form-control-modern',
        'placeholder': 'your.email@example.com'
    }))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={
        'class': 'form-control form-control-modern',
        'placeholder': 'Create a strong password'
    }))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={
        'class': 'form-control form-control-modern',
        'placeholder': 'Repeat your password'
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class MyPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label='Current Password', widget=forms.PasswordInput(attrs={
        'autofocus': 'True',
        'autocomplete': 'current-password',
        'class': 'form-control form-control-modern',
        'placeholder': 'Enter your current password'
    })) 
    new_password1 = forms.CharField(label='New Password', widget=forms.PasswordInput(attrs={
        'autocomplete': 'new-password',
        'class': 'form-control form-control-modern',
        'placeholder': 'Enter your new password'
    }))
    new_password2 = forms.CharField(label='Confirm New Password', widget=forms.PasswordInput(attrs={
        'autocomplete': 'new-password',
        'class': 'form-control form-control-modern',
        'placeholder': 'Confirm your new password'
    }))

class MyPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control form-control-modern',
        'placeholder': 'name@example.com'
    }))

class MySetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'class': 'form-control form-control-modern',
            'placeholder': 'New password'
        })
    )
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'class': 'form-control form-control-modern',
            'placeholder': 'Confirm new password'
        })
    )

class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'locality', 'city', 'mobile', 'state', 'zipcode']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control form-control-modern',
                'placeholder': 'Full name (e.g. Ramesh Patel)'
            }),
            'locality': forms.TextInput(attrs={
                'class': 'form-control form-control-modern',
                'placeholder': 'Flat / House No., Building, Street'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control form-control-modern',
                'placeholder': 'City (e.g. Pune)'
            }),
            'mobile': forms.NumberInput(attrs={
                'class': 'form-control form-control-modern',
                'placeholder': '10-digit mobile number'
            }),
            'state': forms.Select(attrs={
                'class': 'form-select form-control-modern'
            }),
            'zipcode': forms.NumberInput(attrs={
                'class': 'form-control form-control-modern',
                'placeholder': 'PIN code (e.g. 411001)'
            }),
        }