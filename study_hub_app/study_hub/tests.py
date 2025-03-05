from django.test import TestCase
from rest_framework.test import APITestCase, APIClient, force_authenticate
from django.urls import reverse
from rest_framework import status
from .model_factories import *
from .serializers import *

##### API TESTS ####
#confirm that all courses are visible
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
        #self.client.force_login(user=self.teacher1)
        #GET request to endpoint and confirm 200 status
        response = self.client.get(self.getCourseURL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        #confirm both courses are visible
        courses = response.data['results']
        self.assertEqual(len(courses),2)

        #confirm that teacher is accurately listed
        for course in courses:
            self.assertEqual(course['teacher'], self.teacher.id)

#confirm course material is properly uploaded and retrievable
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

class APIGetCourseMaterialTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher = UserFactory(is_teacher=True)
        self.course = CourseFactory(teacher=self.teacher)
        self.viewMaterialURL = reverse('view_course_materials', kwargs={'pk': self.course.pk})

    def tearDown(self):
        User.objects.all().delete()
        Course.objects.all().delete()
        CourseMaterial.objects.all().delete()
        UserFactory.reset_sequence(0)
        CourseFactory.reset_sequence(0)

    def test_view_course_materials(self):
        CourseMaterialFactory(course=self.course)
        CourseMaterialFactory(course=self.course)
        response = self.client.get(self.viewMaterialURL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

#confirm that feedback which is left can be viewed
class APICourseFeedbackTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher = UserFactory(is_teacher=True)
        self.course = CourseFactory(teacher=self.teacher)
        self.student = UserFactory(is_teacher=False)
        self.postFeedbackURL = reverse('post_course_feedback', kwargs={'pk': self.course.pk})
        self.viewFeedbackURL = reverse('view_course_feedback', kwargs={'pk': self.course.pk})

    def tearDown(self):
        User.objects.all().delete()
        Course.objects.all().delete()
        Feedback.objects.all().delete()
        UserFactory.reset_sequence(0)
        CourseFactory.reset_sequence(0)

    def test_post_feedback(self):
        self.client.force_login(user=self.student)
        feedback_data = FeedbackFactory.build(course=self.course, student=self.student)
        data = {
            'rating': feedback_data.rating,
            'content': feedback_data.content
        }
        response = self.client.post(self.postFeedbackURL, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Feedback.objects.filter(course=self.course, student=self.student, content=data['content']).exists())

    def test_view_feedback(self):
        FeedbackFactory(course=self.course)
        FeedbackFactory(course=self.course)
        response = self.client.get(self.viewFeedbackURL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

#user statuses can be posted and retrieved
class APIUserStatusTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.postStatusURL = reverse('post_user_status')
        self.viewStatusURL = reverse('see_user_statuses', kwargs={'pk': self.user.pk})

    def tearDown(self):
        User.objects.all().delete()
        StatusUpdate.objects.all().delete()
        UserFactory.reset_sequence(0)

    def test_post_status(self):
        self.client.force_login(user=self.user)
        data = {'content': 'This is a status update.'}
        response = self.client.post(self.postStatusURL, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(StatusUpdate.objects.filter(user=self.user, content=data['content']).exists())

    def test_view_status(self):
        StatusUpdateFactory(user=self.user)
        StatusUpdateFactory(user=self.user)
        response = self.client.get(self.viewStatusURL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


##### VIEW TESTS #####

#confirm that home page view is locked to specific accounts
class ViewIndexTest(TestCase):
    def setUp(self):
        self.teacher = UserFactory(is_teacher=True)
        self.student = UserFactory(is_teacher=False)

    def tearDown(self):
        User.objects.all().delete()
        EnrollmentNotification.objects.all().delete()
        NewMaterialNotification.objects.all().delete()

        
    def test_index_not_authenticated(self):
        #self.client is in test case
        response = self.client.get(reverse('index'))
        #show that page rendres, but no notifications or links
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.context.get('role', ''), '')

    def test_index_authenticated_teacher(self):
        EnrollmentNotificationFactory(user=self.teacher)
        self.client.force_login(self.teacher)
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        #prove that the context object is returning teacher role
        self.assertEqual(response.context.get('role', ''), 'teacher')
        self.assertTrue(response.context['notifications'].exists())

    def test_index_authenticated_student(self):
        NewMaterialNotificationFactory(user=self.student)
        self.client.force_login(self.student)
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        #prove that the context object is returning student role and notifications are made
        self.assertEqual(response.context.get('role', ''), 'student')
        self.assertTrue(response.context['notifications'].exists())
    
    def test_logout(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        #confirm logout happens correctly by going back to unauth state
        response = self.client.get(reverse('index'))
        self.assertEqual(response.context.get('role', ''), '')

#chat messages can be sent and recieved
class ViewChatWithUserTest(TestCase):
    def setUp(self):
        self.user1 = UserFactory(username='user1')
        self.user2 = UserFactory(username='user2')
        ChatMessageFactory(sender=self.user1, recipient=self.user2)
        ChatMessageFactory(sender=self.user2, recipient=self.user1)
        self.url = reverse('chat_with_user', kwargs={'username': self.user2.username})

    def tearDown(self):
        User.objects.all().delete()
        ChatMessage.objects.all().delete()


    def test_chat_with_user(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        #confirm message is passed to html
        self.assertIn('chat_log', response.context)
        self.assertIn('user_to_message', response.context)

#notifs can be created and deleted
class ViewDeleteNotificationTest(TestCase):
    def setUp(self):
        self.teacher = UserFactory(is_teacher=True)
        self.student = UserFactory(is_teacher=False)
        self.enroll_notif = EnrollmentNotificationFactory(user=self.teacher)
        self.material_notif = NewMaterialNotificationFactory(user=self.student)

    def tearDown(self):
        User.objects.all().delete()
        EnrollmentNotification.objects.all().delete()
        NewMaterialNotification.objects.all().delete()


    def test_delete_enrollment_notification(self):
        self.client.force_login(self.teacher)
        url = reverse('delete_notification', kwargs={'pk': self.enroll_notif.pk})
        response = self.client.get(url)
        #confirm that deletion occurs with appropriate status code for this type of notif
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        #confirm that nothing is there anymore. 
        self.assertFalse(EnrollmentNotification.objects.filter(pk=self.enroll_notif.pk).exists())

    def test_delete_material_notification(self):
        self.client.force_login(self.student)
        url = reverse('delete_notification', kwargs={'pk': self.material_notif.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertFalse(NewMaterialNotification.objects.filter(pk=self.material_notif.pk).exists())

#multiple courses can be viewed by anyone
class ViewCourseCatalogTest(TestCase):
    def setUp(self):
        self.teacher = UserFactory(is_teacher=True)
        CourseFactory(teacher=self.teacher)
        CourseFactory(teacher=self.teacher)

    def tearDown(self):
        User.objects.all().delete()
        Course.objects.all().delete()

    def test_course_catalog(self):
        response = self.client.get(reverse('course_catalog'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('courses', response.context)
        self.assertEqual(len(response.context['courses']), 2)

#can create an account using register view
class ViewRegisterTest(TestCase):
    def setUp(self):
        True #TODO is this setup part required-- put anything here? 

    def tearDown(self):
        User.objects.all().delete()

    def test_registration(self):
        registrationData = {
            'username': 'test',
            'password1': 'P4ssWord!123',
            'password2': 'P4ssWord!123',
            'email': 'test@test.com',
            'name': 'Test Tester',
            'is_teacher': False,
        }
        response = self.client.post(reverse('register'), registrationData)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        #find our user by filtering for the criteria we pass into the post rquest
        self.assertTrue(User.objects.filter(username='test', is_teacher=False, name = 'Test Tester').exists())

#confirm login with dummy details
class LoginTest(TestCase):
    def setUp(self):
        self.password = 'P4ssWord!123'
        self.user = UserFactory()
        self.user.set_password(self.password)
        self.user.save()

    def tearDown(self):
        User.objects.all().delete()

    def test_invalid_login(self):
        loginCredentials = {'username': self.user.username, 'password': '123456'}
        response = self.client.post(reverse('login'), loginCredentials)
        self.assertEqual(response.status_code,  status.HTTP_200_OK) #200 is expected because we're using a catch block to alert the user rather than error out the full page. 
        self.assertIn("Invalid password or username. Please check and try again.", response.context['error']) #should return an error in the context object

    def test_valid_login(self):
        loginCredentials = {'username': self.user.username, 'password': self.password}
        response = self.client.post(reverse('login'), loginCredentials)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND) #should return a success

#confirm that you can enroll in a course
class ViewEnrollInCourseTest(TestCase):
    def setUp(self):
        self.student = UserFactory(is_teacher=False)
        self.course = CourseFactory()
        self.url = reverse('enroll_in_course', kwargs={'pk': self.course.pk})

    def tearDown(self):
        User.objects.all().delete()
        Course.objects.all().delete()
        Enrollment.objects.all().delete()

    def test_enroll_in_course(self):
        self.client.force_login(self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertTrue(Enrollment.objects.filter(course=self.course, student=self.student).exists())

#confirm self unenrollment and teacher unenrollment (block)
class ViewUnenrollFromCourseTest(TestCase):
    def setUp(self):
        self.student1 = UserFactory(is_teacher=False)
        self.student2 =UserFactory(is_teacher=False)
        self.teacher = UserFactory(is_teacher=True)
        self.course = CourseFactory(teacher=self.teacher)
        EnrollmentFactory(student=self.student1, course=self.course)
        
        self.self_unenroll_url = reverse('unenroll_from_course', kwargs={'pk': self.course.pk, 'user_id': self.student1.id})
        self.teacher_unenroll_url = reverse('unenroll_from_course', kwargs={'pk': self.course.pk, 'user_id': self.student2.id})

    def tearDown(self):
        User.objects.all().delete()
        Course.objects.all().delete()
        Enrollment.objects.all().delete()

    def test_unenroll_from_course(self):
        self.client.force_login(self.student1)
        response = self.client.get(self.self_unenroll_url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertFalse(Enrollment.objects.filter(course=self.course, student=self.student1).exists())

    def test_unenroll_by_teacher(self):
        self.client.force_login(self.teacher)
        response = self.client.get(self.teacher_unenroll_url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertFalse(Enrollment.objects.filter(course=self.course, student=self.student2).exists())