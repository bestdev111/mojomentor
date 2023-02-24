from django.shortcuts import render,  redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, Http404
from acc.models import TimeZone, User, Referral
from django.contrib.auth import login, logout  # , authenticate
from django.contrib.auth.decorators import login_required
import json
from django.contrib import messages
import requests
from home.models import ContactUs, DiscountCoupon, Faq
from instructor.models import InstructorProfile
from student.models import StudentProfile
from post.models import Blog, Course, LEVELS_DICT, LANGUAGES_DICT, CourseFaq, Lecture, Topic, Category, CourseReview
from datetime import datetime
from home.models import Supportticket
from datetime import datetime, date
from utility.pdf import generate_invoice
from django.db import connection
from django.views.decorators.csrf import csrf_exempt

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from utility.helpers import gen_random_str

from django.conf import settings
import random
from django.db.models import Q

# Create your views here.
def index(request):
    categories = Category.objects.filter(status=True)
    context = {
        "categories": []
    }
    for category in categories:
        context["categories"].append({
            "id": category.id, "title": category.title,
            "courses": Course.objects.filter(category_id=category.id)
        })
    return render(request, "home/index.html", context)


def course_detail(request, slug):
    try:
        course = Course.objects.select_related('user').get(slug=slug)
    except Course.DoesNotExist:
        raise Http404
    lecture_list = Lecture.objects.filter(course_id=course.id)
    pre_url = request.scheme + '://' + request.get_host() + '/instructor/'
    context = {
        "course": course, "level": LEVELS_DICT[course.level],
        "language": LANGUAGES_DICT[course.language],
        "faqs": CourseFaq.objects.filter(course_id=course.id),
        "lectures": [],
        "profile": InstructorProfile.objects.get(user_id=course.user_id),
        "instructor_url": pre_url+course.user.username,
        "curr_user_review": None,
    }
    for lecture in lecture_list:
        context["lectures"].append({
            "id": lecture.id, "name": lecture.name,
            "topics": Topic.objects.filter(lecture_id=lecture.id)
        })
    if request.user.is_authenticated:
        try:
            context["curr_user_review"] = CourseReview.objects.get(course_id=course.id, user_id=request.user.id)
        except CourseReview.DoesNotExist:
            pass
    with connection.cursor() as cursor:
        cursor.execute(
            f"""select u.id, u.username, u.profile_pic, r.text, r.stars, 5 - r.stars as not_stars from course_reviews r
            inner join acc_user u on r.user_id=u.id where r.course_id={course.id} order by r.id desc"""
        )
        # columns = [col[0] for col in cursor.description]
        context["reviews"] = cursor.fetchall()
        cursor.execute(
            f"""select COUNT(id) AS count, SUM(stars) AS total_stars from course_reviews where course_id={course.id}"""
        )
        final_review = cursor.fetchone()
        if final_review[1] is None or final_review[0] == 0:
            context["total_stars"] = 0
        else:
            context["total_stars"] = round(final_review[1] / final_review[0], 1)
    return render(request, "home/course-detail.html", context)


@login_required
def create_course_review(request, id):
    if request.method != "POST":
        return JsonResponse({"msg": "Method not allowed"}, status=405)
    course = get_object_or_404(Course, id=id)
    data = json.loads(request.body)
    print(data)
    try:
        CourseReview.objects.get(course_id=course.id, user_id=request.user.id)
        return JsonResponse({"msg": "Review already exists.", "data": {}}, status=401)
    except CourseReview.DoesNotExist:
        CourseReview.objects.create(
            course_id=course.id, user_id=request.user.id,
            stars=data['stars'], text=data['review']
        )
        return JsonResponse({"msg": "Review posted successfully.", "data": {}}, status=200)


def instructor_list(request):
    user_id = request.user.id if request.user.id else 0
    with connection.cursor() as cursor:
        cursor.execute(
            f"""select u.id, u.username, u.profile_pic,
            (select count(id) from followers where to_user_id=u.id and from_user_id={user_id} limit 1) as followed
            from acc_user u where role=3 and is_active=true """
        )
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    return JsonResponse({"msg": "Success.", "data": {"columns": columns, "rows": rows}}, status=200)


def auth_login(request):
    if request.method == "GET":
        return render(request, "home/sign-in.html", {'G_CLIENT_ID': settings.GOOGLE_LOGIN_CLIENT_ID, 'F_APP_ID': settings.FACEBOOK_LOGIN_APP_ID})

    elif request.method == "POST":
        data = json.loads(request.body)
        email = data["email"].strip()
        try:
            user = User.objects.get(email=email)
            if user.is_active:
                if user.check_password(data["password"]):
                    login(request, user)
                    messages.success(request, 'Logged in successfully.')
                    return JsonResponse({"msg": "Success", "data": {"role": user.role}}, status=200)
                else:
                    return JsonResponse({"msg": "Username or Password does not matched."}, status=401)
            else:
                return JsonResponse({"msg": "Your account has been blocked by admin. Please contact admin to unblock your account."}, status=401)
        except User.DoesNotExist:
            return JsonResponse({"msg": f'No user found for email "{email}"'}, status=401)
    else:
        return HttpResponse("Method not allowed", status=405)


def auth_logout(request):
    logout(request)
    return redirect('/')


def gen_user_name(email, fname='', lname=''):
    fname = fname.lower()
    lname = lname.lower()
    uname = email.split('@')[0] if email else f"{fname}{lname}{random.randint(1,9999)}"
    while True:
        try:
            User.objects.get(username=uname)
            uname = f"{fname}{lname}{random.randint(1,9999)}"
            continue
        except User.DoesNotExist:
            break
    return uname


def register(request):
    if request.method == "GET":
        return render(request, "home/sign-up.html", {'G_CLIENT_ID': settings.GOOGLE_LOGIN_CLIENT_ID, 'F_APP_ID': settings.FACEBOOK_LOGIN_APP_ID})
    elif request.method == "POST":
        data = json.loads(request.body)
        email = data["email"].strip()
        role = data["role"]
        if role != '3' and role != '4':
            return JsonResponse({"massage": "Bad request"}, status=400)
        try:
            user = User.objects.get(email=email)
            return JsonResponse({"msg": f'User Already exits for email "{email}"'}, status=409)
        except User.DoesNotExist:
            user = User.objects.create_user(
                email=email,
                password=data["password"],
                username=gen_user_name(email),
                role=int(role)
            )
            if user.role == 3:
                InstructorProfile.objects.create(user_id=user.id)
            elif user.role == 4:
                StudentProfile.objects.create(user_id=user.id)
            # code for handing Referral system
            refer_by = request.GET.get('refer_by')
            if refer_by is not None:
                try:
                    refer_by_user = User.objects.get(username=refer_by)
                    Referral.objects.create(refer_by_id = refer_by_user.id,refer_to_id=user.id)
                except User.DoesNotExist:
                    pass
            login(request, user)
            return JsonResponse({"massage": "Registered successfully", "data": {"role": user.role}}, status=201)
    else:
        raise Http404


def forgot_pwd(request):
    if request.method == "GET":
        return render(request, "home/forgot-password.html")


def login_using_facebook(request):
    if request.method == "POST":
        data = json.loads(request.body)
        res = requests.get(
            f"https://graph.facebook.com/{data['userID']}?access_token={data['accessToken']}&fields=id,name,email"
        )
        if res.status_code == 200:
            fb_data = res.json()
            social_id = "F-" + fb_data['id']
            if 'email' in fb_data and fb_data['email']:
                email = fb_data['email']
            else:
                email = None
                
            try:
                user = User.objects.get(social_id = social_id)
            except User.DoesNotExist:
                user = User.objects.create_user(
                    username=gen_user_name(email, fb_data['name'], ''),
                    first_name=fb_data['name'], role=4, email = email,
                    password=gen_random_str(),
                )
                StudentProfile.objects.create(user_id=user.id)
            if user.is_active:
                login(request, user)
                messages.success(request, 'Login successfully.')
                return JsonResponse({"msg": "Logged in using Facebook successfully", "data": {"role": user.role}}, status=200)
            else:
                return JsonResponse({"msg": "Your account has been blocked by admin. Please contact admin to unblock your account."}, status=401)
        else:
            return JsonResponse({"msg": "Facebook verification failed"}, status=res.status_code)
    else:
        raise Http404

def login_using_google(request):
    if request.method == "POST":
        data = json.loads(request.body)
        try:
            # Specify the CLIENT_ID of the app that accesses the backend:
            idinfo = id_token.verify_oauth2_token(data['credential'], google_requests.Request(), settings.GOOGLE_LOGIN_CLIENT_ID)

            # Or, if multiple clients access the backend server:
            # idinfo = id_token.verify_oauth2_token(token, google_requests.Request())
            # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
            #     raise ValueError('Could not verify audience.')

            # If auth request is from a G Suite domain:
            # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
            #     raise ValueError('Wrong hosted domain.')

            # ID token is valid. Get the user's Google Account ID from the decoded token.
            # userid = idinfo['sub']
        except ValueError:
            # Invalid token
            return JsonResponse({"msg": "Invalid google token"}, status=400)
        
        social_id = "G-" + idinfo['sub']
        
        try:
            user = User.objects.get(Q(social_id = social_id) | Q(email=idinfo['email']))
            if not user.social_id:
                user.social_id = social_id
                user.email_verified = True
                user.save()
        except User.DoesNotExist:
            user = User.objects.create_user(
                social_id = social_id,
                username = gen_user_name(idinfo['email'], idinfo['given_name'], idinfo['family_name']),
                email = idinfo['email'],
                first_name = idinfo['given_name'],
                last_name = idinfo['family_name'],
                role=4,
                password=gen_random_str(),
                email_verified = True
            )
            StudentProfile.objects.create(user_id=user.id)
        if user.is_active:
            login(request, user)
            messages.success(request, 'Login successfully.')
            return JsonResponse({"msg": "Logged in using google successfully", "data": {"role": user.role}}, status=200)
        else:
            return JsonResponse({"msg": "Your account has been blocked by admin. Please contact admin to unblock your account."}, status=401)    
    else:
        return HttpResponse("Method not allowed.", status=405)

def faqs(request):
    a = Faq.objects.filter(status=True).order_by("-id")
    return render(request, 'home/faq.html', {"faqss": a})


def about_us(request):
    return render(request, 'home/about-us.html')


def contact_us(request):
    if request.method == 'GET':
        return render(request, 'home/contact-us.html')
    elif request.method == 'POST':
        Supportticket.objects.create(
            name=request.POST['name'],
            email=request.POST['email'],
            issue=request.POST['issue'],
        )
        messages.success(
            request, 'your token submitted successfully. Admin will contact you soon.')
        return redirect('/contact-us')
    else:
        raise Http404


def blogs(request):
    blogs = Blog.objects.select_related('user').filter(status=True)
    return render(request, 'home/blogs.html', {'blogs': blogs})


def blog_detail(request, slug):
    try:
        blog = Blog.objects.select_related('user').get(slug=slug)
    except Blog.DoesNotExist:
        raise Http404
    # print(datetime.now() - blog.created_on)
    return render(request, 'home/blog-detail.html', {'blog': blog})


# def set_time_zone_time(request):
#     html = ''
#     time_zones = TimeZone.objects.all()
#     for zone in time_zones:
#         try:
#             hr, min = zone.utc_offset[1:].split(':')
#             utc_offset_min = (int(hr) * 60) + int(min)
#             utc_offset_min = f"{zone.utc_offset[0]}{utc_offset_min}"
#             html += f"{zone.utc_offset} => {utc_offset_min} <br />"
#             zone.utc_offset_min = utc_offset_min
#             zone.save()
#         except:
#             continue
#     return HttpResponse(html)


@login_required
def course_checkout(request, id):
    course = get_object_or_404(Course, id=id)
    if course.user_id == request.user.id:
        raise Http404
    price = course.discount_price if course.discount_price else course.price
    coupons = DiscountCoupon.objects.raw(
        f"select * from discount_coupons where exp_date >= '{datetime.utcnow().strftime('%Y-%m-%d')}' AND status = true"
    )
    return render(request, "home/course-checkout.html", {
        "price": price, 'course': course, 'coupons': coupons
    })


def check_coupon(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        coupon = DiscountCoupon.objects.filter(
            code=data['coupon_code'].strip()).order_by("-id").first()
        if coupon:
            if coupon.exp_date < datetime.utcnow().date() or coupon.status == False:
                return JsonResponse({"msg": "Coupon expired."}, status=401)
            course = get_object_or_404(Course, id=data['course_id'])
            price = course.discount_price if course.discount_price else course.price
            discount = price * (coupon.percent/100)
            price = price - discount
            return JsonResponse({
                "msg": "Coupon Applied.",
                "data": {
                    "eff_price": price, "discount": discount, "coupon_id": coupon.id,
                    "title": f"{coupon.percent}% discount"
                }
            }, status=200)
        else:
            return JsonResponse({"msg": "Invalid Coupon."}, status=404)
    else:
        return JsonResponse({"msg": "Method not allowed"}, status=405)


def download_pdf(request):
    return generate_invoice()


@csrf_exempt
def test_link(request):
    if request.method == 'GET':
        return render(request, 'home/test-link.html')
    elif request.method == 'POST':
        print(request.POST)
        return HttpResponse("sdfsdf")