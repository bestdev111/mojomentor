from django.db import models

# constants
STATUS = ((False, 'InActive'), (True, 'Active'))


# Create your models here.
class Faq(models.Model):
    class Meta:
        db_table = "faqs"
    ques = models.CharField(max_length=255)
    ans = models.TextField()
    status = models.BooleanField(choices=STATUS, default=True)
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)


class ContactUs(models.Model):
    class Meta:
        db_table = "contact_us"
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)


class DiscountCoupon(models.Model):
    class Meta:
        db_table = "discount_coupons"
    code = models.CharField(max_length=15)
    percent = models.SmallIntegerField()
    status = models.BooleanField(choices=STATUS, default=True)
    exp_date = models.DateField()
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)


class Supportticket(models.Model):
    class Meta:
        db_table = "support_tickets"
    name = models.CharField(max_length=50)
    email = models.EmailField()
    issue = models.TextField()
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)
