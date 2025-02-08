from django import forms
from django.contrib.auth import get_user_model #uses our abstract user class
from django.contrib.auth.forms import UserCreationForm

from django.forms import ModelForm
from .models import *

User = get_user_model()

class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2') #password 2 is defulat ofr password validation

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('is_teacher', )
