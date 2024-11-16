from django import forms
from .models import UserType

# Function to populate the selectable user_type options in RegistrationForm 
def get_user_types():
    return UserType.objects.all()

class LoginForm(forms.Form):
    email = forms.CharField(widget = forms.EmailInput(attrs = {'class': 'form-control', 'placeholder' : 'Email'}))
    password = forms.CharField(widget = forms.PasswordInput(attrs = {'class': 'form-control', 'placeholder' : 'Password'}))

class RegistrationForm(forms.Form):
    email = forms.CharField(widget = forms.EmailInput(attrs = {'class': 'form-control', 'placeholder' : 'Email'}))
    associated_company = forms.CharField(widget=forms.TextInput(attrs = {'class': 'form-control', 'placeholder' : 'Associated Company'}))
    password = forms.CharField(widget = forms.PasswordInput(attrs = {'class': 'form-control', 'placeholder' : 'Password'}))
    password_confirmation = forms.CharField(widget = forms.PasswordInput(attrs = {'class': 'form-control', 'placeholder' : 'Confirm Password'}))
    user_type = forms.ModelChoiceField(
        # Get all existing UserType records and add as options to select element
        queryset = get_user_types(),
        empty_label = 'User Registraion Type'
    )



         

    
