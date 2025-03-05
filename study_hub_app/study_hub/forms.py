from django import forms
from django.contrib.auth import get_user_model #uses our abstract user class
from django.contrib.auth.forms import UserCreationForm

from PIL import Image

from django.forms import ModelForm
from .models import *
import datetime 

User = get_user_model()

class UserForm(UserCreationForm):
    name = forms.CharField(required=True)
    photo = forms.ImageField(required=False)
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'name', 'photo') #password 2 is defulat for password validation

    
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


class UpdateCourseMaterial(forms.ModelForm):

    title = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 1, 'placeholder': 'Brief Title of the Assignment'}), label='Assignment Title')
    file = forms.FileField(widget=forms.ClearableFileInput(attrs={'class': 'form-control'}), label='File Upload', required=True)  #upload optional

    #forms do not have consolidated date time, so track separt3e
    assignment_due_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), label='Assignment Due Date')
    assignment_due_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}), label='Assignment Due Time')

    class Meta:
        model = CourseMaterial
        fields = ('title', 'file')

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('assignment_due_date')
        time = cleaned_data.get('assignment_due_time')
        if date and time:
            #combine for later use
            assignment_due_datetime = datetime.datetime.combine(date, time)
            cleaned_data['assignment_due_datetime'] = assignment_due_datetime
        else:
            raise forms.ValidationError("Both date and time are required.")

        return cleaned_data

class CreateCourse(forms.ModelForm):

    title = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 1, 'placeholder': 'Brief Title of the Course'}), label='Course Name')
    description =  forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe the course in a few sentences'}), label='Description')
    class Meta:
        model = Course
        fields = ('title', 'description') #TODO is teacher required based on how this is accessed? 