from django.urls import path
from . import views

urlpatterns = [
    # path('', views.home, name="home"),
    path('pay-course', views.pay_course, name="pay_course"),
    # path('create-checkout-session', views.create_checkout_session,
    #      name='create_checkout_session'),
    path('stripe-webhook', views.stripe_webhook, name='stripe_webhook'),
    path("course/success/<str:code>", views.course_pay_success),
    path("course/cancel/<str:code>", views.course_pay_cancel),
]
