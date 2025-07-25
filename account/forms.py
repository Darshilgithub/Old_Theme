from django import forms
import re
from vt_site.models import Plan
from .models import User

ALLOWED_EMAIL_DOMAINS = ['vulnix.org', 'gmail.com']

def validate_email_domain(email):
    try:
        domain = email.split('@')[1]
    except IndexError:
        raise forms.ValidationError("Invalid email format.")
    if domain.lower() not in ALLOWED_EMAIL_DOMAINS:
        raise forms.ValidationError("Only emails from vulnix.org or gmail.com are allowed.")
    return email

class UserForm(forms.ModelForm):
    pic = forms.ImageField(
        widget=forms.FileInput(attrs={'class': 'form-control shadow-none'}),
        label='Profile Pic'
    )
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter Username',
            'class': 'form-control shadow-none',
            'autocomplete': 'on',
            'onpaste': 'return false;',
            'oncopy': 'return false;',
            'onkeypress': "return /^[a-zA-Z0-9_]+$/.test(event.key);"
        }),
        label='Username'
    )
    
    mobile = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter Mobile Number',
            'class': 'form-control shadow-none',
            'autocomplete': 'on',
            'disabled': True,
            'onpaste': 'return false;',
            'oncopy': 'return false;',
            'onkeypress': "return /^[0-9]+$/.test(event.key);"
        }),
        label='Mobile Number'
    )
    
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter First Name',
            'class': 'form-control shadow-none',
            'autocomplete': 'on',
            'onpaste': 'return false;',
            'oncopy': 'return false;',
            'onkeypress': "return /^[a-zA-Z]+$/.test(event.key);"
        }),
        label='First Name'
    )
    
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter Last Name',
            'class': 'form-control shadow-none',
            'autocomplete': 'on',
            'onpaste': 'return false;',
            'oncopy': 'return false;',
            'onkeypress': "return /^[a-zA-Z]+$/.test(event.key);"
        }),
        label='Last Name',
        required=False
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter email',
            'class': 'form-control shadow-none',
            'autocomplete': 'on',
            'disabled': True,  # If you want this field uneditable
            'onpaste': 'return false;',
            'oncopy': 'return false;'
        }),
        label='Email'
    )
    
    current_plan = forms.ModelChoiceField(
        queryset=Plan.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select form-control shadow-none', 'disabled': True}),
        label='Current Plan'
    )
    
    coins = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control shadow-none', 'autocomplete': 'on', 'disabled': True}),
        label='Coins'
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'mobile', 'email', 'pic', 'current_plan', 'coins']

    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise forms.ValidationError("Only letters, numbers, and underscores are allowed.")
        return username

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        if not re.match(r'^[a-zA-Z]+$', first_name):
            raise forms.ValidationError("Only letters are allowed.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name', '')
        if last_name and not re.match(r'^[a-zA-Z]+$', last_name):
            raise forms.ValidationError("Only letters are allowed.")
        return last_name

    def clean_email(self):
        email = self.cleaned_data['email']
        return validate_email_domain(email)


class UserForm1(forms.ModelForm):
    mobile = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter Mobile Number',
            'class': 'form-control shadow-none',
            'autocomplete': 'on',
            'onpaste': 'return false;',
            'oncopy': 'return false;',
            'onkeypress': "return /^[0-9]+$/.test(event.key);"
        }),
        label='Mobile Number'
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter email',
            'class': 'form-control shadow-none',
            'autocomplete': 'on',
            'onpaste': 'return false;',
            'oncopy': 'return false;'
        }),
        label='Email'
    )

    class Meta:
        model = User
        fields = ['mobile', 'email']

    def clean_email(self):
        email = self.cleaned_data['email']
        return validate_email_domain(email)

class UserForm1(forms.ModelForm):
    mobile = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Enter Mobile Number', 'class': 'form-control shadow-none', 'autocomplete' : 'on'}),label='Mobile Number')
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Enter email', 'class': 'form-control shadow-none', 'autocomplete' : 'on'}),label='email')
    
    class Meta:
        model = User
        fields = ['mobile', 'email']
