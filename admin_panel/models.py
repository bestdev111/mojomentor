from django.db import models


# Create your models here.
class Setting(models.Model):
    class Meta:
        db_table = "settings"
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)