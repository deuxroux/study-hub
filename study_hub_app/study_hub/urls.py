from django.urls import include, path
from . import views
from . import api

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('api/allCourses', api.AllCourses.as_view(), name = 'course_information'),
    path('api/addCourse', api.AddCourse.as_view(), name = 'add_course'),
    path('api/enroll/<int:pk>', api.Enroll, name = 'enrollment'),
    path('api/addCourseMaterial/<int:pk>', api.AddCourseMaterials.as_view(), name='add_materials'),
    path('api/viewCourseMaterials/<int:pk>', api.viewCourseMaterials, name='view_course_materials')
]