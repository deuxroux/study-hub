from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect, get_object_or_404
from rest_framework import status, generics, mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .models import *
from .serializers import *

from rest_framework.decorators import api_view

class ListPagination(PageNumberPagination):
    page_size = 8 #set consistent entries per page for large returns

#see all courses
class ViewCourseInformation(mixins.RetrieveModelMixin,
                    generics.GenericAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = ListPagination

#add a single course
class AddCourse(mixins.CreateModelMixin,
                        mixins.UpdateModelMixin,
                        generics.GenericAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    #should only accessible by teachers
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

#see all courses
class AllCourses(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer 
    pagination_class = ListPagination

class PostStatus(APIView):
    def post(self, request, format = None):
        user = request.user
        serializer = StatusUpdateSerializer(data = request.data)

        # some logic to ensure that all the details for the data post was correct
        if serializer.is_valid():
            serializer.save(user = user)
            return Response({'status': 'status posted successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

class SeeUserStatuses(APIView):
    def get (self, request, pk, format = None):
        user= get_object_or_404(User, pk = pk)
        statuses = StatusUpdate.objects.filter(user = user)
        serializedStatus = StatusUpdateSerializer(statuses, many = True)

        return Response(serializedStatus.data)
    

class GetCourseMaterials(APIView):
    pagination_class = ListPagination
    def  get(self, request,pk, format=None):
        course = get_object_or_404(Course, pk= pk)
        courseMaterials = CourseMaterial.objects.filter(course=course)
        serializedMaterials = CourseMaterialSerializer(courseMaterials, many=True)
        return Response(serializedMaterials.data)

class AddCourseMaterials(mixins.RetrieveModelMixin,
                            mixins.CreateModelMixin,
                            mixins.UpdateModelMixin,
                            generics.GenericAPIView):
    queryset = CourseMaterial.objects.all()
    serializer_class = CourseMaterialSerializer
    #get should only be accessible for enrolled students and teachers
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    #put only accessible by teachers
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class PostCourseFeedback(APIView):
    def post(self, request, pk, format = None):
        user = request.user
        course = get_object_or_404(Course, pk = pk)
        serializer = FeedbackSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save(student = user, course = course)
            return Response({'status': 'feedback posted successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class ViewCourseFeedback(APIView):
    def get (self, request, pk, format = None):
        course= get_object_or_404(Course, pk = pk)
        feedback = Feedback.objects.filter(course = course)
        serializedFeedback = FeedbackSerializer(feedback, many = True)

        return Response(serializedFeedback.data)
    

#enroll handles enrollment, logic for attempted repeat enroll, and unenrollment
@api_view(['POST', 'DELETE'])
def Enroll(request, pk):
    user = request.user
    course = get_object_or_404(Course, pk=pk)

    #logic to manage an already enrolled entity
    if request.method == 'POST':
        enrollment = Enrollment.objects.get_or_create(student = user, course= course)
        if enrollment:
            return Response({'status': 'enrolled'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'status': 'already enrolled'}, status=status.HTTP_200_OK)
    
    #unenroll endpoint
    if request.method == 'DELETE':
        enrollment = Enrollment.objects.filter(student=user, course=course)
        if enrollment.exists():
            enrollment.delete()
            return Response({'status': 'unenrolled'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'status': 'not enrolled'}, status=status.HTTP_404_NOT_FOUND)