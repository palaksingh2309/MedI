from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name', 'phone_number', 'date_of_birth')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'date_of_birth', 'profile_picture')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'date_of_birth', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control-file'}),
        }


from dashboard.models import HealthProfile

class HealthProfileForm(forms.ModelForm):
    class Meta:
        model = HealthProfile
        fields = [
            'height', 'weight', 'age', 'gender', 'blood_group', 
            'allergies', 'existing_conditions', 'emergency_contact', 
            'fitness_goal', 'water_goal', 'sleep_goal'
        ]
        widgets = {
            'height': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Height in cm', 'step': '0.1'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Weight in kg', 'step': '0.1'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Age in years'}),
            'gender': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Gender (e.g. Female, Male)'}),
            'blood_group': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Blood Group (e.g. A+)'}),
            'allergies': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Known allergies or None...', 'rows': 2}),
            'existing_conditions': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Existing medical conditions...', 'rows': 2}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact name / Phone number'}),
            'fitness_goal': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Fitness goals (e.g. Weight loss, Active living)'}),
            'water_goal': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Water goal in ml'}),
            'sleep_goal': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Sleep goal in hours', 'step': '0.5'}),
        }
