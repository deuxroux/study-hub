from .models import *
from random import choice, uniform,randint
import string
import factory


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}") # use lambda function to increment user1, user2, etc. 
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@website.com")
    name = factory.Faker('name')
    is_teacher= factory.LazyFunction(lambda: choice([True, False]))

class CourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Course

    title = factory.Faker('sentence', nb_words = 3)
    description = factory.Faker('sentence', nb_words = 20) #arb 20 word sentence for description
    teacher = factory.SubFactory(UserFactory, is_teacher= True) #create a user who is a teacher

    #bc students is many to many??

    
class EnrollmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Enrollment

    student = factory.SubFactory(UserFactory, is_teacher= False) #create a user who is not a teacher
    date_enrolled = factory.Faker('past_date') # arbitrary past date
    course = factory.SubFactory(CourseFactory)

    
class FeedbackFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Feedback
    
    course = factory.SubFactory(CourseFactory)
    rating = factory.LazyFunction(lambda: randint(1,5))
    student = factory.SubFactory(UserFactory, is_teacher = False)
    content = factory.Faker('sentence', nb_words = 20) #review content is a few sentences
    date_posted = factory.Faker('past_date') 

class StatusUpdateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StatusUpdate

    user = factory.SubFactory(UserFactory)
    content = factory.Faker('sentence', nb_words = 20) 
    timestamp = factory.Faker('past_datetime', start_date="-10d") #arbitrary 10 days ago


class CourseMaterialFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CourseMaterial
    course = factory.SubFactory(CourseFactory)
    title =  factory.Faker('sentence', nb_words = 5)   
    uploaded_at = factory.Faker('past_datetime', start_date="-10d") #arbitrary 10 days ago
    assignment_due_date = factory.Faker('future')  

class ChatMessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ChatMessage
    
    sender = factory.SubFactory(UserFactory)
    recipient = factory.SubFactory(UserFactory)
    message = factory.Faker('sentence', nb_words = 10)
    timestamp =  factory.Faker('past_datetime', start_date="-10d") #arbitrary 10 days ago

class EnrollmentNotificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EnrollmentNotification

    message = factory.Faker('sentence', nb_words = 10)
    timestamp =factory.Faker('past_datetime', start_date="-10d") #arbitrary 10 days ago
    user = factory.SubFactory(UserFactory, is_teacher = True)
    
class NewMaterialNotificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = NewMaterialNotification

    message = factory.Faker('sentence', nb_words = 10)
    timestamp =factory.Faker('past_datetime', start_date="-10d") #arbitrary 10 days ago
    user = factory.SubFactory(UserFactory, is_teacher = False)
