from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Max
from django.http import HttpResponseForbidden
from django.utils.timezone import now
from .models import *
from .forms import *
from .serializers import *

# Create your views here.
def index(request):
    return render(request, 'study_hub/index.html')

def user_logout(request):
    logout(request)
    return redirect('/')

def course_catalog(request):
    context ={}
    courseData = Course.objects.annotate(
        num_students=Count('students', distinct=True), #distinct must be true to avoid duplicates across other models during join
        avg_rating=Avg('feedback__rating')
    ).all() #Use django features for annotate to substitute for join methods

    context = {
        'courses': courseData
    }

    return render(request, 'study_hub/course_catalog.html', context)

def register(request):
    registered = False

    if request.method == 'POST':
        user_form = UserForm(request.POST,request.FILES) #deal with image too
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit = False) # do not commit until we get the is_teacher field
            user.is_teacher=profile_form.cleaned_data.get('is_teacher')

            #TODO image processing? 

            user.save()

            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, 'study_hub/register.html', {'user_form': user_form,
                                                       'profile_form': profile_form,
                                                       'registered': registered})

def user_login(request):
    context = {}
    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')


        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return redirect('/')
            else:
                context['error'] = "Session Inactive. Log in Again" #TODO figure out what error messge to put
        else:
            context['error'] = "Invalid password or username. Please check and try again."

    return render(request, 'study_hub/login.html', context )

@login_required
def my_learning_view(request):
    user = request.user

    course_data = Course.objects.filter(students=user).annotate(
        latest_assignment=Max('materials__title', filter=models.Q(materials__assignment_due_date__gte=now())), #perform a query for the assignment with the nearest due date
        assignment_due=Max('materials__assignment_due_date', filter=models.Q(materials__assignment_due_date__gte=now()))
    ).order_by('title')

    context = {'user_courses': course_data}
    return render(request, 'study_hub/my_learning.html', context)

@login_required
def my_teaching_view(request):
    user = request.user

    course_data = Course.objects.filter(teacher=user).annotate(
        num_students=Count('students', distinct=True), #distinct must be true to avoid duplicates across other models during join
        avg_rating=Avg('feedback__rating'),
        latest_assignment=Max('materials__title', filter=models.Q(materials__assignment_due_date__gte=now())), #perform a query for the assignment with the nearest due date
        assignment_due=Max('materials__assignment_due_date', filter=models.Q(materials__assignment_due_date__gte=now()))
    ).order_by('title')

    context = {'user_courses': course_data}
    return render(request, 'study_hub/my_teaching.html', context)

@login_required
def add_new_course(request):
    user = request.user
    if not user.is_teacher:
        return HttpResponseForbidden('You are not authorized to create new courses.')
    
    if request.method =='POST':
        form = CreateCourse(request.POST)
        if form.is_valid():
            new_course=form.save(commit=False)
            new_course.teacher=user
            new_course.save()
            return redirect(my_teaching_view)
    else:
        form=CreateCourse()
    
    return render(request, 'study_hub/new_course.html', {'form':form, 'user_is_teacher': user.is_teacher})


@login_required
def course_edit_view(request, pk):
    #course data
    course = get_object_or_404(Course, pk = pk)
    materials = CourseMaterial.objects.filter(course=course).order_by('-uploaded_at')
    enrolled_students = User.objects.filter(enrollment__course=course).distinct()

    user = request.user
    user_is_teacher = Course.objects.filter(teacher=user, id=pk).exists()

    context = {
        'course': course,
        'materials': materials,
        'user_is_teacher': user_is_teacher,
        'enrolled_students': enrolled_students
    }
    return render(request, 'study_hub/course_edit.html', context)

@login_required
def course_material_upload(request, pk):
    #course data
    course = get_object_or_404(Course, pk = pk)

    if request.method == 'POST':
        form = UpdateCourseMaterial(request.POST, request.FILES)
        if form.is_valid():
            course_material = form.save(commit=False) #don't save until we deal with the date time issue
            course_material.assignment_due_Date = form.cleaned_data.get('assignment_due_datetime')
            course_material.course = course
            course_material.save()
            return redirect(course_edit_view, pk = course.pk)
    else:
        form = UpdateCourseMaterial()

    return render(request, 'study_hub/course_material_upload.html', {'form':form, 'course':course})


@login_required
def course_view(request, pk):
    #course data
    course = get_object_or_404(Course, pk = pk)
    # course materials
    materials = CourseMaterial.objects.filter(course=course).order_by('-uploaded_at')


    user = request.user
    user_is_enrolled = Enrollment.objects.filter(student=user, course=course).exists()
    user_can_enroll = not user.is_teacher and not user_is_enrolled
    enrolled_students = User.objects.filter(enrollment__course=course).distinct()

    context = {
        'course': course,
        'materials': materials,
        'user_is_enrolled': user_is_enrolled,
        'user_can_enroll': user_can_enroll,
        'enrolled_students': enrolled_students,
        'user':user
    }
    return render(request, 'study_hub/course_detail.html', context)

@login_required
def enroll_in_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    user = request.user

    #employ a second check in case the url is accessed elsewhere
    if not user.is_teacher:
        Enrollment.objects.get_or_create(student = user, course = course)
        return redirect(course_view, pk = course.pk)

@login_required
def unenroll_from_course(request, pk, user_id):
    is_teacher = False
    course = get_object_or_404(Course, pk= pk)
    if user_id == request.user.id or request.user.is_teacher:
        user = get_object_or_404(User, id =user_id)
        if request.user.is_teacher:
            is_teacher = True
        Enrollment.objects.filter(student= user, course= course).delete() #TODO does this logic handle the case that a user is not enrolled?
    else:
        return redirect(index) #TODO figure out how to raise an error... this clauses is just to prevent someone trying to unenroll manually. 
    
    if is_teacher:
        return redirect(course_edit_view, pk = course.pk)
    else:
        return redirect(course_view, pk = course.pk)

@login_required
def user_profile_page(request, username):
    profile = get_object_or_404(User, username = username)
    is_own_profile = request.user == profile # see if the person viewing owns the profile and thus is able to make status updates
    form = None

    if is_own_profile and request.method == 'POST':
        form = StatusUpdateForm(request.POST)
        if form.is_valid():
            serializer = StatusUpdateSerializer(data = {'content': form.cleaned_data['content']})
            if serializer.is_valid():
                serializer.save(user = request.user)
                return redirect(user_profile_page, username = username)
            else:
                print(serializer.errors)
    elif is_own_profile:
        form = StatusUpdateForm()

    statuses = StatusUpdate.objects.filter(user=profile).order_by('-timestamp') #sort descending time

    role = "Teacher" if profile.is_teacher else "Student" #delineate the user status for display later

    context = {
        'user': profile,
        'role':role, 
        'statuses': statuses,
        'form': form,
        'is_own_profile' : is_own_profile
    }
    return render(request, 'study_hub/user_profile.html', context)

@login_required
def feedback_view(request,pk):
    course = get_object_or_404(Course, pk = pk)
    if request.method == 'POST':
        form = LeaveFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.course = course
            feedback.student = request.user
            feedback.save()
            return redirect(feedback_view, pk = course.pk)
    else:
        form = LeaveFeedbackForm()
    
    prev_feedback = Feedback.objects.filter(course=course).order_by('-date_posted')
    context = {'form':form, 'course':course, 'feedbacks': prev_feedback}

    return render(request, 'study_hub/feedback.html', context)
