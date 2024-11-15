from django import forms

class LoginForm(forms.Form):
    email = forms.CharField(widget = forms.EmailInput(attrs = {'class': 'form-control', 'placeholder' : 'Email'}))
    password = forms.CharField(widget = forms.PasswordInput(attrs = {'class': 'form-control', 'placeholder' : 'Password'}) )