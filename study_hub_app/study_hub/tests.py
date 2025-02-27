from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status
from .model_factories import *
from .serializers import *

##### API TESTS ####
class APICourseViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher = UserFactory(is_teacher= True)
        self.course1 = CourseFactory(teacher = self.teacher)
        self.course2 = CourseFactory(teacher = self.teacher)
        self.getCourseURL = reverse('course_information')

    def tearDown(self):
         User.objects.all().delete()
         Course.objects.all().delete()
         UserFactory.reset_sequence(0)
         CourseFactory.reset_sequence(0)

    def test_course_details(self):
        #self.client.force_authenticate(user=self.teacher1)
        #GET request to endpoint and confirm 200 status
        response = self.client.get(self.getCourseURL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        #confirm both courses are visible
        courses = response.data['results']
        self.assertEqual(len(courses),2)

        #confirm that teacher is accurately listed
        for course in courses:
            self.assertEqual(course['teacher'], self.teacher.id)

class APICourseMaterialTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher = UserFactory(is_teacher= True)
        self.addCourseURL = reverse('add_course')

    def tearDown(self):
         User.objects.all().delete()
         Course.objects.all().delete()
         UserFactory.reset_sequence(0)
         CourseFactory.reset_sequence(0)

    def test_add_course(self):
        #use build method to populate json later without populating database
        course_data = CourseFactory.build(teacher = self.teacher)

        api_json = {
            'title': course_data.title,
            'description': course_data.description,
            'teacher': course_data.teacher.id
        }

        response = self.client.post(self.addCourseURL, api_json, format = 'json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        #confirm that the api payload exists in database
        self.assertTrue(Course.objects.filter(title=api_json['title'], description=api_json['description'], teacher=self.teacher).exists())

##### SERIALIZER TESTS #####