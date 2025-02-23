#general model imports
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import MaxValueValidator, MinValueValidator #used for star rating system validation

#notifs imports
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    # start with default user model but with an field "is_teacher field" to distingursh either way
    is_teacher = models.BooleanField(default=False)

    name = models.CharField(max_length = 255)
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)


    #had to add in order to debug
    groups = models.ManyToManyField(
        Group,
        blank=True,
        related_name="study_hub_user_set", 
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name="study_hub_user_set",
        related_query_name="user",
    )

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses_taught')
    students = models.ManyToManyField(User, through='Enrollment', related_name='courses_enrolled')
    
    #way to get a course title from outside later
    def __str__(self):
        return self.title
    

class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_enrolled = models.DateTimeField(auto_now_add=True)


class Feedback(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE,)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null = True)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)

class StatusUpdate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='status_updates')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class CourseMaterial(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='course_materials/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    assignment_due_date = models.DateTimeField(null=True, blank=True)


class ChatMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    #add code to help debug
    def __str__(self):
        return f"Message from {self.sender.username} to {self.recipient.username} at {self.timestamp}"

class EnrollmentNotification(models.Model):
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollment_notifications')
    #add code to help debug
    def __str__(self):
        return f"new enrollment notification for {self.user.username} at {self.timestamp}"
 

class NewMaterialNotification(models.Model):
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='material_notifications')
    #add code to help debug
    def __str__(self):
        return f"Notification for new material, alerting: {self.user.username} at {self.timestamp}"

# Notify teacher for student enroll
@receiver(post_save, sender=Enrollment)
def notify_teacher_on_enrollment(sender, instance, created, **kwargs):
    if created:
        message = f"{instance.student.username} has enrolled in your course '{instance.course.title}'."
        EnrollmentNotification.objects.create(
            message=message,
            user=instance.course.teacher
        )

@receiver(post_save, sender=CourseMaterial)
def notify_students_on_new_material(sender, instance, created, **kwargs):
    if created:
        students_to_notify = instance.course.students.all() #get all affected studentcs
        message = f"There is a new assignment titled: {instance.title} posted in your course page-- {instance.course.title}. Please complete the assignment by {instance.assignment_due_date}.  Go to the class page to review."
        
        #push notification to each

        for student in students_to_notify:
            NewMaterialNotification.objects.create(
                message=message,
                user=student
            )

