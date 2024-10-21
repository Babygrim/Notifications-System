from django import forms 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignupForm(UserCreationForm):
    username = forms.CharField(help_text='', label='Username')
    password1 = forms.CharField(widget=forms.PasswordInput, help_text='', label='Password')
    password2 = forms.CharField(widget=forms.PasswordInput, help_text='', label='Confirm Password')

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)