#from turtle import update
from . import views
from django.urls import path

urlpatterns = [
    path('', views.index),
    path('dashboard', views.dashboard, name='ad_dashboard'),
    path('login', views.auth_login, name='ad_login'),
    # ---------------- categories ---------------
    path('categories', views.categories, name='ad_categories'),
    path('category-list', views.category_list, name='ad_category_list'),
    path('category/<int:id>/edit', views.edit_category, name='ad_edit_category'),
    path('category/create', views.create_category, name='ad_create_category'),
    # ---------------- coupons ---------------
    path('coupons', views.coupons, name='ad_coupons'),
    path('coupon-list', views.coupon_list, name='ad_coupon_list'),
    path('coupon/<int:id>/edit', views.edit_coupon, name='ad_edit_coupon'),
    path('coupon/create', views.create_coupon, name='ad_create_coupon'),
    path('coupon/<int:id>/delete', views.delete_coupon, name='ad_delete_coupon'),
    # ---------------- students ---------------
    path('students', views.students, name='ad_students'),
    path('student-list', views.student_list, name='ad_student_list'),
    path('student/<int:id>/view', views.view_student, name='ad_view_student'),
    # ---------------- users ---------------
    path('user/<int:id>/chats', views.user_chats, name='ad_user_chats'),
    path('user/<int:curr_id>/get-chats/<int:to_id>', views.user_get_chats, name='ad_user_get_chats'),
    # ---------------- instructors ---------------
    path('instructors', views.instructors, name='ad_instructors'),
    path('instructor-list', views.instructor_list, name='ad_instructor_list'),
    path('instructor/<int:id>/view', views.view_instructor, name='ad_view_instructor'),
    # ---------------- coupons ---------------
    path('faqs', views.faqs, name='ad_faqs'),
    path('faq-list', views.faq_list, name='ad_faq_list'),
    path('faq/<int:id>/edit', views.edit_faq, name='ad_edit_faq'),
    path('faq/create', views.create_faq, name='ad_create_faq'),
    path('faq/<int:id>/delete', views.delete_faq, name='ad_delete_faq'),
    # ---------------- settings ---------------
    path('settings', views.settings, name='ad_settings'),
]
