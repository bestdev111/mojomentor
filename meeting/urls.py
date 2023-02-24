from django.urls import path
from . import views

urlpatterns = [
    path('book-appointment', views.book_appointment, name='book_appointment'),
    path('get-appointment/<int:id>/modify-info', views.get_appoint_modify_info, name='get_appoint_modify_info'),
    path('appointment/<int:id>/rating', views.appointment_rating, name='appointment_rating'),
    path('appointment/<int:id>',views.appointment, name="appointment_page")
]
