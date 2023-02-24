from email.policy import default
from random import choices
from django.db import models
from acc.models import User
from utility.helpers import seconds_to_hms
from django.db import connection
# constants
STATUS = ((False, 'InActive'), (True, 'Active'))

LEVELS = (
    ('all_level', 'All level'), ('beginner', 'Beginner'),
    ('intermediate', 'Intermediate'), ('advance', 'Advance')
)
LEVELS_DICT = {
    'all_level': 'All level', 'beginner': 'Beginner',
    'intermediate': 'Intermediate', 'advance': 'Advance'
}

LANGUAGES = (
    ('english', 'English'), ('german', 'German'), ('french', 'French'),
    ('hindi', 'Hindi')
)
LANGUAGES_DICT = {
    'english': 'English', 'german': 'German', 'french': 'French',
    'hindi': 'Hindi'
}

COURSE_STATUS = ((0, 'Pending'), (1, 'Active'), (2, 'InActive'))
# Create your models here.


class Category(models.Model):
    class Meta:
        db_table = 'categories'
    title = models.CharField(max_length=255)
    status = models.BooleanField(choices=STATUS, default=True)
    updated_on = models.DateTimeField(auto_now=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True)


class Course(models.Model):
    class Meta:
        db_table = 'courses'
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    about = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    status = models.SmallIntegerField(choices=COURSE_STATUS, default=0)
    category = models.ForeignKey(
        Category,  on_delete=models.PROTECT, null=True)
    level = models.CharField(max_length=20, choices=LEVELS)
    language = models.CharField(max_length=20, choices=LANGUAGES)
    featured = models.BooleanField(default=False)
    time = models.CharField(max_length=50)
    total_lecture = models.SmallIntegerField()
    price = models.FloatField()
    discount_price = models.FloatField()
    description = models.TextField()
    image = models.ImageField(upload_to='courses/', null=True)
    video = models.FileField(upload_to='courses/', null=True)
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

    @property
    def duration(self):
        with connection.cursor() as cursor:
            cursor.execute(f"""select sum(duration) from topics where lecture_id in
            (select id from lectures where course_id={self.id}) """)
            duration = cursor.fetchone()[0]
        duration = duration if duration != None else 0
        hours, mins, secs = seconds_to_hms(duration)
        return f"{hours}h {mins}m" if hours else f"{mins}m"

    @property
    def no_of_lecture(self):
        return Lecture.objects.filter(course_id=self.id).count()

    @property
    def show_level(self):
        return LEVELS_DICT[self.level]

    @property
    def discount_percent(self):
        return 100 - ((self.discount_price / self.price) * 100) if self.discount_price else 0

class CourseReview(models.Model):
    class Meta:
        db_table = 'course_reviews'
    course = models.ForeignKey(Course,  on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    stars = models.SmallIntegerField()
    text = models.TextField()
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

class CourseFaq(models.Model):
    class Meta:
        db_table = 'course_faqs'
    course = models.ForeignKey(Course,  on_delete=models.CASCADE)
    ques = models.CharField(max_length=255)
    ans = models.TextField()
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)


class Lecture(models.Model):
    class Meta:
        db_table = 'lectures'
    course = models.ForeignKey(Course,  on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)


class Topic(models.Model):
    class Meta:
        db_table = 'topics'
    lecture = models.ForeignKey(Lecture,  on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    premium = models.BooleanField(default=False)
    description = models.TextField()
    video = models.FileField(upload_to='course-videos/', null=True)
    duration = models.FloatField(default=0)
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

    @property
    def duration1(self):
        hours, mins, secs = seconds_to_hms(self.duration)
        return f"{str(hours).zfill(2)}:{str(mins).zfill(2)}:{str(secs).zfill(2)}"

    @property
    def duration2(self):
        hours, mins, secs = seconds_to_hms(self.duration)
        time_str = f"{hours}h {mins}m {secs}s" if hours else f"{mins}m {secs}s"
        return time_str


class Question(models.Model):
    class Meta:
        db_table = 'questions'
    text = models.TextField()
    category = models.ForeignKey(
        Category,  on_delete=models.PROTECT, null=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    status = models.BooleanField(choices=STATUS, default=True)
    updated_on = models.DateTimeField(auto_now=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True)


class Answer(models.Model):
    class Meta:
        db_table = 'answers'
    text = models.TextField()
    question = models.ForeignKey(Question,  on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    status = models.BooleanField(choices=STATUS, default=True)
    updated_on = models.DateTimeField(auto_now=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True)


class Like(models.Model):
    class Meta:
        db_table = 'likes'
    question = models.ForeignKey(Question,  on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)


class AnsVote(models.Model):
    class Meta:
        db_table = 'ans_votes'
    answer = models.ForeignKey(Answer,  on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)


class AnsEndorse(models.Model):
    class Meta:
        db_table = 'ans_endorses'
    answer = models.ForeignKey(Answer,  on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)


class Blog(models.Model):
    class Meta:
        db_table = 'blogs'
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    title = models.CharField(max_length=255)
    about = models.TextField()
    slug = models.SlugField(max_length=255, unique=True)
    body = models.TextField()
    image = models.ImageField(upload_to='blogs/', null=True)
    video = models.FileField(upload_to='blogs/', null=True)
    status = models.BooleanField(choices=STATUS, default=True)
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)


class AnsDisapprove(models.Model):
    class Meta:
        db_table = 'ans_disapproves'
    answer = models.ForeignKey(Answer,  on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

class LookingForMentor(models.Model):
    class Meta:
        db_table = 'looking_for_mentors'
    title = models.CharField(max_length=255)
    text = models.TextField()
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

class LookingForWork(models.Model):
    class Meta:
        db_table = 'looking_for_works'
    title = models.CharField(max_length=255)
    text = models.TextField()
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)
