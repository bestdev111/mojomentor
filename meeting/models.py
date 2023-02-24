from django.db import models
from acc.models import User


# constants
APPOINTMENT_STATUS = ((0, 'Pending'), (1, 'Accepted'), (2, 'Declined'))


# Create your models here.
class Appointment(models.Model):
    class Meta:
        db_table = 'appointments'
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    instructor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='appointment_instructor'
    )
    start_time = models.CharField(max_length=5)
    end_time = models.CharField(max_length=5)
    status = models.SmallIntegerField(choices=APPOINTMENT_STATUS, default=0)
    url = models.URLField()
    date = models.DateField()
    modify_req = models.BooleanField(default=False)
    
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

class AppointmentModifyReq(models.Model):
    class Meta:
        db_table = 'appointment_modify_reqs'
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    modify_text= models.TextField(null=True)
    status = models.SmallIntegerField(choices=APPOINTMENT_STATUS, default=0)
    date = models.DateField()
    start_time = models.CharField(max_length=5)
    end_time = models.CharField(max_length=5)
    
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)


class AppointmentReview(models.Model):
    class Meta:
        db_table = 'appointment_reviews'
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    stars = models.SmallIntegerField()
    text = models.TextField()
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)