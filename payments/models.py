from django.db import models
from acc.models import User
from post.models import Course

# constants
PAY_STATUS = ((0, 'Pending'), (1, 'Paid'), (2, 'Expired'))


# Create your models here.
class Order(models.Model):
    class Meta:
        db_table = "orders"
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stripe_session_id = models.CharField(max_length=255, null=True)
    pay_status = models.SmallIntegerField(choices=PAY_STATUS)
    amount = models.FloatField()
    payer_email = models.CharField(max_length=255, null=True)
    payer_name = models.CharField(max_length=255, null=True)
    product_type = models.CharField(max_length=20, null=True)
    product_id=models.PositiveBigIntegerField(null=True)
    code = models.CharField(max_length=255, null=True)  # for one time only

    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)


class CoursePayment(models.Model):
    class Meta:
        db_table = "course_payments"
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    order = models.ForeignKey(Order, on_delete=models.PROTECT)

    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)


