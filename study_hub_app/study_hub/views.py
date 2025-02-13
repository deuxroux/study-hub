from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from .models import *
from .forms import *
from .api import *

# Create your views here.
def index(request):
    return render(request, 'study_hub/index.html')

def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')


def user_login(request):
    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                return HttpResponse("Error") #TO DO figure out what error messge to put
        else:
            return HttpResponse("Invalid password or username. Please check and try again.")
    else:
        return render(request, 'study_hub/login.html', )

def user_profile_page(request, username):
    user = get_object_or_404(User, username = username)
    statuses = StatusUpdate.objects.filter(user=user).order_by('-timestamp') #sort descending time

    role = "Teacher" if user.is_teacher else "Student" #delineate the user status for display later

    context = {
        'user': user,
        'role':role, 
        'statuses': statuses,
    }
    return render(request, 'study_hub/user_profile.html', context)

def register(request):
    registered = False

    if request.method == 'POST':
        user_form = UserForm(request.POST,request.FILES) #deal with image too
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user

            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, 'study_hub/register.html', {'user_form': user_form,
                                                       'profile_form': profile_form,
                                                       'registered': registered})
