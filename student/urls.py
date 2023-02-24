from . import views
from django.urls import path

urlpatterns = [
    path('', views.index),
    path('dashboard', views.dashboard, name='stu_dashboard'),
    path('profile', views.profile, name='stu_profile'),
    path('appointments', views.appointments, name='stu_appointments'),
    path('appointment-list', views.appointment_list, name='stu_appointment_list'),
    path('update-appointment', views.update_appointment, name='stu_update_appointment'),
    path('courses', views.courses, name='stu_courses'),
    path('course_list', views.course_list, name='stu_course_list')
]
