from . import views
from django.urls import path

urlpatterns = [
    path('', views.index),
    path('dashboard', views.dashboard, name='inst_dashboard'),
    path('profile', views.profile, name='inst_profile'),
    path('course/create', views.create_course, name='create_course'),
    path('course/list', views.course_list, name='inst_course_list'),
    path('course/<int:id>/edit', views.edit_course, name='edit_course'),
    path(
        'course/<int:course_id>/lecture/create', views.create_lecture, name='create_lecture'
    ),
    path(
        'lecture/<int:lecture_id>/topic/create', views.create_topic, name='create_topic'
    ),
    path(
        'course/<int:course_id>/course-faq/create', views.create_course_faq, name='create_course_faq'
    ),
    path(
        'course/<int:course_id>/media', views.course_media, name='course_media'
    ),
    path('appointments', views.appointments, name='inst_appointments'),
    path('appointment-list', views.appointment_list, name='inst_appointment_list'),
    path('update-appointment', views.update_appointment, name='inst_update_appointment'),
    path('reviews', views.reviews, name='inst_reviews'),
    path('review-list', views.review_list, name='inst_review_list'),
    path('<str:username>', views.inst_detail, name='inst_detail'),
]
