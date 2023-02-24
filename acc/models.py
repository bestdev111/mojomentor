from email.policy import default
from django.db import models
from django.contrib.auth.models import AbstractUser
from ws.models import MSG_TYPE


# constants
ROLES = (
    (1, 'Super Admin'), (2, 'Admin/Manager'), (3, 'Mentor'), (4, 'User/Student')
)


# Create your models here.
class Country(models.Model):
    class Meta:
        db_table = 'countries'
    iso = models.CharField(max_length=2, null=True)
    name = models.CharField(max_length=100, null=True)
    nicename = models.CharField(max_length=100, null=True)
    iso3 = models.CharField(max_length=3, null=True)
    numcode = models.SmallIntegerField(null=True)
    phonecode = models.SmallIntegerField(null=True)

class TimeZone(models.Model):
    class Meta:
        db_table = 'time_zones'
    name = models.CharField(max_length=100)
    utc_offset = models.CharField(max_length=8)
    utc_offset_min = models.FloatField(default=0, null=True)
    is_dst = models.BooleanField()


class User(AbstractUser):
    profile_pic = models.ImageField(upload_to='profiles/', null=True)
    role = models.SmallIntegerField(default=4, choices=ROLES)
    email_verified = models.BooleanField(default=False)
    country = models.ForeignKey(
        Country, on_delete=models.PROTECT, null=True
    )
    phone_no = models.CharField(max_length=10, null=True)
    time_zone = models.ForeignKey(
        TimeZone, on_delete=models.PROTECT, null=True
    )
    social_id = models.CharField(max_length=50, unique=True, null=True)


class ChatUser(models.Model):
    class Meta:
        db_table = 'chat_users'
    user1 = models.ForeignKey(User, on_delete=models.CASCADE)
    user2 = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user2'
    )
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)


class Chat(models.Model):
    class Meta:
        db_table = 'chats'
    user1 = models.ForeignKey(User, on_delete=models.CASCADE)
    user2 = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='chat_user2'
    )
    type = models.SmallIntegerField(choices=MSG_TYPE)
    msg = models.TextField()
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)


class Education(models.Model):
    class Meta:
        db_table = 'educations'
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)


class Follower(models.Model):
    class Meta:
        db_table = 'followers'
    to_user = models.ForeignKey(User, on_delete=models.CASCADE)
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followed_by_user')
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)


class Referral(models.Model):
    class Meta:
        db_table = 'referrals'
    refer_to = models.ForeignKey(User, on_delete=models.PROTECT, related_name='refer_to_user')
    refer_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='refer_by_user')
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)
