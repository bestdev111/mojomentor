from . import views
from django.urls import path

urlpatterns = [
    path('', views.index, name='home'),
    path("course/<str:slug>", views.course_detail, name='course_detail'),
    path('course/create-review/<int:id>', views.create_course_review, name='create_review'),
    path("instructor-list", views.instructor_list, name='instructor_list'),
    path("faqs", views.faqs, name='faqs'),
    path("login", views.auth_login, name='login'),
    path("logout", views.auth_logout, name='logout'),
    path("register", views.register, name='register'),
    path("forgot-password", views.forgot_pwd, name='forgot_pwd'),
    path(
        'login-using-facebook', views.login_using_facebook, name='login_using_facebook'
    ),
    path(
        'login-using-google', views.login_using_google, name='login_using_google'
    ),
    path('about-us', views.about_us, name='about_us'),
    path('contact-us', views.contact_us, name='contact_us'),
    path('blogs', views.blogs, name='blogs'),
    path("blog/<str:slug>", views.blog_detail, name='blog_detail'),
    # path('set-time-zone-time',views.set_time_zone_time),
    path("course/<int:id>/checkout", views.course_checkout, name='course_checkout'),
    path("check-coupon", views.check_coupon, name='check_coupon'),
    path("download-pdf", views.download_pdf, name='download_pdf'),
         
    path("test-link", views.test_link, name='test_link'),
]
