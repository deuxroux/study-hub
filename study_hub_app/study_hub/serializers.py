from rest_framework import serializers
from .models import *

#for each model, initialize a serializer class that we can build up on for CRUD operations
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_teacher', 'groups', 'user_permissions']


class CourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'teacher', 'students']

class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'date_enrolled']
        read_only_fields = ['id', 'date_posted']

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'course', 'student', 'content', 'date_posted']
        read_only_fields = ['id', 'course', 'student', 'date_posted']
    
class StatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusUpdate
        fields = ['id', 'user', 'content', 'timestamp']
        read_only_fields = ['id', 'user', 'timestamp']
        
class CourseMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseMaterial
        fields = ['id', 'course', 'title', 'file', 'uploaded_at']

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'sender', 'recipient', 'message', 'timestamp']