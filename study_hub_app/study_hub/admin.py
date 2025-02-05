from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(Feedback)
admin.site.register(ChatMessage)
admin.site.register(StatusUpdate)
admin.site.register(CourseMaterial)