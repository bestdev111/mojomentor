from django.db import models
from acc.models import User


# Create your models here.
class StudentProfile(models.Model):
    class Meta:
        db_table = 'student_profiles'
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)


class StudentReview(models.Model):
    class Meta:
        db_table = 'student_reviews'
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='student_review_by')
    stars = models.SmallIntegerField()
    text = models.TextField()
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)