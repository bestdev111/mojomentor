from django.db import models
from acc.models import User


# Create your models here.
class InstructorProfile(models.Model):
    class Meta:
        db_table = 'instructor_profiles'
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about = models.TextField(null=True)
    twitter = models.CharField(max_length=255, null=True)
    instagram = models.CharField(max_length=255, null=True)
    facebook = models.CharField(max_length=255, null=True)
    linkedin = models.CharField(max_length=255, null=True)
    youtube = models.CharField(max_length=255, null=True)
    start_time = models.CharField(max_length=5, null=True)
    end_time = models.CharField(max_length=5, null=True)
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

class InstructorReview(models.Model):
    class Meta:
        db_table = 'instructor_reviews'
    instructor = models.ForeignKey(User, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='review_by')
    stars = models.SmallIntegerField()
    text = models.TextField()
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)