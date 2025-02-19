from django.urls import include, path
from . import views
from . import api

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('user/<str:username>/', views.user_profile_page, name='user_profile'),
    path('course-catalog/', views.course_catalog, name = 'course_catalog'),
    path('course/<int:pk>', views.course_view, name = 'course_view'),
    path('feedback/<int:pk>', views.feedback_view, name='leave_feedback'),
    path('enroll/<int:pk>', views.enroll_in_course, name='enroll_in_course'),
    path('unenroll/<int:pk>', views.unenroll_from_course, name='unenroll_from_course'),
    path('my-learning/', views.my_learning_view, name = 'my_learning'),
    path('edit-course/<int:pk>', views.course_edit_view, name = 'course_edit_view'),
    path('add-course-material/<int:pk>', views.course_material_upload, name = 'course_material_upload'),

    #API routes for debugging
    path('api/allCourses', api.AllCourses.as_view(), name = 'course_information'),
    path('api/addCourse', api.AddCourse.as_view(), name = 'add_course'),
    path('api/enroll/<int:pk>', api.Enroll, name = 'enrollment'),
    path('api/add-course-material/<int:pk>', api.AddCourseMaterials.as_view(), name='add_materials'),
    path('api/view-course-material/<int:pk>', api.GetCourseMaterials.as_view(), name='view_course_materials'),
    path('api/post-feedback/<int:pk>', api.PostCourseFeedback.as_view(), name='post_course_feedback'),
    path('api/view-feedback/<int:pk>', api.ViewCourseFeedback.as_view(), name='view_course_feedback'),
    path('api/post-status', api.PostStatus.as_view(), name = 'post_user_status'),
    path('api/view-status/<int:pk>', api.SeeUserStatuses.as_view(), name= 'see_user_statuses'),
]