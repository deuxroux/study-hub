from django import forms
from django.contrib.auth import get_user_model #uses our abstract user class
from django.contrib.auth.forms import UserCreationForm

from PIL import Image

from django.forms import ModelForm
from .models import *

User = get_user_model()

class UserForm(UserCreationForm):
    name = forms.CharField(required=True)
    photo = forms.ImageField(required=False)
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'name', 'photo') #password 2 is defulat ofr password validation

    
class UserProfileForm(forms.ModelForm):
    is_teacher = forms.BooleanField(label='Please check this box if you are an educator.', required=False)

    class Meta:
        model = User
        fields = ('is_teacher', )

class StatusUpdateForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Whats on your mind?'}), label='Post a Status')
    class Meta:
        model = StatusUpdate
        fields = ('content')

class LeaveFeedbackForm(forms.ModelForm):
    rating = forms.HiddenInput()
    content =  forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'How is this Course?'}), label='Leave Feedback')
    class Meta:
        model = Feedback
        fields = ('rating', 'content')