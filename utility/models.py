from django.db import models
from acc.models import User


# Create your models here.
class LinkToken(models.Model):
    class Meta:
        db_table = 'link_tokens'
    user = models.ForeignKey(User,  on_delete=models.CASCADE)
    token = models.CharField(max_length=100)
    expire_in = models.CharField(max_length=30)
