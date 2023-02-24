import os
from django.shortcuts import render, redirect, get_object_or_404
from acc.models import ChatUser, Follower, TimeZone, User
from instructor.models import InstructorProfile
from meeting.models import Appointment, AppointmentModifyReq
from post.models import Category, LEVELS, LANGUAGES, Course, CourseFaq, Topic, Lecture
from utility.decorators import instructor_required
from django.http import HttpResponse, JsonResponse
import json
from django.db import connection
from django.utils.text import slugify
import itertools
from moviepy.editor import VideoFileClip
from django.db.models import Q
from datetime import date, timedelta, datetime
from utility.helpers import datetime_str_to_utc_datetime_str, mins_to_time, time_offset_to_mins, time_to_mins, time_str_to_utc_time_str, utc_time_str_to_time_str


# Create your views here.
@instructor_required
def index(request):
    return redirect('/')


@instructor_required
def dashboard(request):
    return render(request, 'instructor/inst-dashboard.html')


@instructor_required
def profile(request):
    if request.method == 'GET':
        with connection.cursor() as cursor:
            cursor.execute(f"select id, name from countries")
            countries = cursor.fetchall()
            cursor.execute(f"select id, name, utc_offset from time_zones")
            time_zones = cursor.fetchall()
        profile = InstructorProfile.objects.get(user_id=request.user.id)
        if request.user.time_zone:
            time_zone_id = request.user.time_zone_id
            utc_offset = request.user.time_zone.utc_offset
        else:
            time_zone_id = 47
            utc_offset = "+00:00"
        start_time = utc_time_str_to_time_str(
            profile.start_time, utc_offset) if profile.start_time else ''
        end_time = utc_time_str_to_time_str(
            profile.end_time, utc_offset) if profile.end_time else ''
        return render(request, 'instructor/inst-profile.html', {
            'countries': countries, "profile": profile, 'time_zones': time_zones,
            'time_zone_id': time_zone_id, 'start_time': start_time, 'end_time': end_time,
        })
    elif request.method == 'POST':
        data = json.loads(request.body)
        if data['info_type'] == 'about':
            profile = InstructorProfile.objects.get(user_id=request.user.id)
            utc_offset = request.user.time_zone.utc_offset if request.user.time_zone else "+00:00"
            # print(time_to_mins(data['start_time']) + diff_min)
            profile.about = data['about']
            profile.twitter = data['twitter']
            profile.instagram = data['instagram']
            profile.facebook = data['facebook']
            profile.linkedin = data['linkedin']
            profile.youtube = data['youtube']
            profile.start_time = time_str_to_utc_time_str(
                data['start_time'], utc_offset)
            profile.end_time = time_str_to_utc_time_str(
                data['end_time'], utc_offset)
            profile.save()
            return JsonResponse({'msg': 'Information updated successfully.'}, status=200)
    else:
        return JsonResponse({"msg": "Method not allowed"}, status=405)


@instructor_required
def course_list(request):
    courses = Course.objects.filter(user_id=request.user.id).order_by('-id')
    return render(request, 'instructor/inst-course-list.html', {'courses': courses})


@instructor_required
def create_course(request):
    if request.method == 'GET':
        context = {
            "categories": Category.objects.filter(status=True).order_by("-id"),
            "languages": LANGUAGES,
            "levels": LEVELS
        }
        return render(request, 'instructor/inst-create-course.html', context)
    elif request.method == 'POST':
        # ---------- generating slug ----------
        slug_candidate = slug_original = slugify(request.POST['title'])
        for i in itertools.count(1):
            if not Course.objects.filter(slug=slug_candidate).exists():
                break
            slug_candidate = '{}-{}'.format(slug_original, i)
        # -------------------------------------
        course = Course.objects.create(
            user_id=request.user.id,
            title=request.POST['title'],
            slug=slug_candidate,
            about=request.POST['about'],
            category_id=request.POST['category'],
            level=request.POST['level'],
            language=request.POST['language'],
            featured=True if 'featured' in request.POST else False,
            time=request.POST['time'],
            total_lecture=request.POST['total_lecture'],
            price=request.POST['price'],
            discount_price=request.POST['discount_price'],
            description=request.POST['description'],
        )
        return redirect(f'/instructor/course/{course.id}/edit')
    else:
        return HttpResponse("Method not allowed", status=405)


@instructor_required
def edit_course(request, id):
    course = get_object_or_404(Course, id=id)
    if course.user_id != request.user.id:
        return HttpResponse("Access denied", status=401)
    if request.method == 'GET':
        lectures = Lecture.objects.filter(course_id=course.id)
        lectureList = []
        for lecture in lectures:
            lectureList.append({
                "id": lecture.id,
                "name": lecture.name,
                "topics": Topic.objects.filter(lecture_id=lecture.id)
            })
        context = {
            "categories": Category.objects.filter(status=True).order_by("-id"),
            "languages": LANGUAGES,
            "levels": LEVELS,
            "course": course,
            "lectures": lectureList,
            "course_faqs": CourseFaq.objects.filter(course_id=course.id),
        }
        return render(request, 'instructor/inst-create-course.html', context)
    elif request.method == 'POST':
        if request.POST['info_type'] == 'basic_type':
            course.title = request.POST['title']
            course.about = request.POST['about']
            course.category_id = request.POST['category']
            course.level = request.POST['level']
            course.language = request.POST['language']
            course.featured = True if 'featured' in request.POST else False
            course.time = request.POST['time']
            course.total_lecture = request.POST['total_lecture']
            course.price = request.POST['price']
            course.discount_price = request.POST['discount_price']
            course.description = request.POST['description']
            course.save()
        return redirect(f'/instructor/course/{id}/edit?step=2')
    else:
        return HttpResponse("Method not allowed", status=405)


@instructor_required
def create_lecture(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if course.user_id != request.user.id:
        return HttpResponse("Access denied", status=401)
    if request.method == 'POST':
        data = json.loads(request.body)
        lecture = Lecture.objects.create(
            course_id=course.id,
            name=data['name']
        )
        return JsonResponse({"msg": "Lecture created successfully", "data": {"id": lecture.id}}, status=201)
    else:
        return HttpResponse("Method not allowed", status=405)


@instructor_required
def create_topic(request, lecture_id):
    lecture = get_object_or_404(Lecture, id=lecture_id)
    if lecture.course.user_id != request.user.id:
        return HttpResponse("Access denied", status=401)
    if request.method == 'POST':
        topic = Topic.objects.create(
            lecture_id=lecture.id,
            name=request.POST['name'],
            description=request.POST['description'],
            premium=request.POST['premium'],
            video=request.FILES['video'] if 'video' in request.FILES else None,
        )
        if 'video' in request.FILES:
            video = VideoFileClip(topic.video.path)
            topic.duration = video.duration
            topic.save()
            video.close()
        return JsonResponse({"msg": "Topic created successfully", "data": {"id": topic.id}}, status=201)
    else:
        return HttpResponse("Method not allowed", status=405)


@instructor_required
def create_course_faq(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if course.user_id != request.user.id:
        return HttpResponse("Access denied", status=401)
    if request.method == 'POST':
        data = json.loads(request.body)
        course_faq = CourseFaq.objects.create(
            course_id=course.id, ques=data['question'], ans=data['answer']
        )
        return JsonResponse({"msg": "FAQ created successfully", "data": {"id": course_faq.id}}, status=201)
    else:
        return HttpResponse("Method not allowed", status=405)


@instructor_required
def course_media(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if course.user_id != request.user.id:
        return HttpResponse("Access denied", status=401)
    if request.method == 'POST':
        if 'video' in request.FILES:
            if course.video:
                os.remove(course.video.path)
            course.video = request.FILES['video']
        if 'image' in request.FILES:
            if course.image:
                os.remove(course.image.path)
            course.image = request.FILES['image']
        course.save()
        return JsonResponse({"msg": "Course media updated successfully", "data": {"id": course.id}}, status=200)
    else:
        return HttpResponse("Method not allowed", status=405)


def inst_detail(request, username):
    instructor = get_object_or_404(User, username=username)
    profile = get_object_or_404(InstructorProfile, user_id=instructor.id)
    chat_link = '/login'
    if request.user.is_authenticated:
        chat_link = f'/account/create-chat-user/{instructor.id}'
        chat_exits = ChatUser.objects.raw(
            f"""select * from chat_users where (user1_id={instructor.id} and user2_id={request.user.id})
            or (user1_id={request.user.id} and user2_id={instructor.id})
            """
        )
        if chat_exits:
            chat_link = '/account/chats'
        if request.user.time_zone:
            time_zone = request.user.time_zone
            utc_offset = time_zone.utc_offset
            time_zone_name = time_zone.name
            start_time = utc_time_str_to_time_str(
                profile.start_time, utc_offset) if profile.start_time else ''
            end_time = utc_time_str_to_time_str(
                profile.end_time, utc_offset) if profile.end_time else ''
        else:
            time_zone_name = "UTC"
            start_time = profile.start_time
            end_time = profile.end_time

        try:
            Follower.objects.get(to_user_id=instructor.id, from_user_id=request.user.id)
            followed = 1
        except Follower.DoesNotExist:
            followed = 0
    else:
        time_zone_name = "UTC"
        start_time = profile.start_time
        end_time = profile.end_time

        followed = 0
    # offset_mins = 0
    # if instructor.time_zone:
    #     offset_mins = time_offset_to_mins(instructor.time_zone.utc_offset)
    # start_time = time_to_mins(profile.start_time) + offset_mins
    # end_time = time_to_mins(profile.end_time) + offset_mins
    tomorrow = date.today() + timedelta(days=1)
    return render(request, 'instructor/inst-detail.html', {
        'instructor': instructor, 'profile': profile, 'chat_link': chat_link,
        'start_time': start_time, 'end_time': end_time, 'tomorrow': tomorrow.strftime('%Y-%m-%d'),
        'time_zone_name': time_zone_name, 'followed': followed
    })


@instructor_required
def appointments(request):
    return render(request, 'instructor/inst-appointments.html')


@instructor_required
def appointment_list(request):
    with connection.cursor() as cursor:
        limit = f"OFFSET {request.GET['offset']} LIMIT {request.GET['no_of_row']}"
        common_query = f"FROM appointments ap INNER JOIN acc_user u ON ap.student_id=u.id WHERE ap.instructor_id={request.user.id}"
        cursor.execute(f"SELECT COUNT(ap.id) AS count {common_query}")
        count = cursor.fetchone()[0]
        cursor.execute(
            f"""SELECT ap.id, ap.date, ap.start_time, ap.end_time, ap.url, ap.student_id,
            u.username, ap.status, ap.modify_req {common_query}
            ORDER BY id DESC {limit}"""
        )
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    return JsonResponse({"msg": "success", "data": {"columns": columns, "rows": rows, "count": count}})


@instructor_required
def update_appointment(request):
    data = json.loads(request.body)
    appointment = get_object_or_404(Appointment, id=data['id'])
    if appointment.instructor_id != request.user.id or appointment.status != 0 or appointment.modify_req:
        return JsonResponse({"msg": "Access denied"} , status=401)
    msg = 'Success'
    if data['type'] == 'accept':
        appointment.status = 1
        msg = 'Appointment accepted successfully.'
    elif data['type'] == 'decline':
        appointment.status = 2
        msg = 'Appointment declined successfully.'
    elif data['type'] == 'modify':
        appointment.modify_req = True
        msg = 'Appointment modification request submitted successfully.'

        if request.user.time_zone:
            time_zone = request.user.time_zone
            utc_offset = time_zone.utc_offset
            meet_date, start_time = datetime_str_to_utc_datetime_str(data['date'], data['start_time'], utc_offset) if data['start_time'] else ''
            end_time = time_str_to_utc_time_str(data['end_time'], utc_offset) if data['end_time'] else ''
        else:
            start_time = data['start_time']
            end_time = data['end_time']
            meet_date = data['date']
            
        AppointmentModifyReq.objects.create(
            appointment_id=appointment.id,
            start_time = start_time,
            end_time = end_time,
            date = meet_date,
            modify_text = data['modify_text']
        )
    appointment.save()
    return JsonResponse({"msg": msg, "data": {"status": appointment.status, 'modify_req': appointment.modify_req}}, status=200)


@instructor_required
def reviews(request):
    return render(request, 'instructor/inst-reviews.html')


@instructor_required
def review_list(request):
    user_id = request.user.id
    condition = f'WHERE r.instructor_id={user_id}'
    limit = f"OFFSET {request.GET['offset']} LIMIT {request.GET['no_of_row']}"
    with connection.cursor() as cursor:
        common_query = f"from instructor_reviews r inner join acc_user u on r.user_id=u.id {condition}"
        cursor.execute(
            f"""SELECT COUNT(r.id) AS count {common_query};""")
        count = cursor.fetchone()[0]
        cursor.execute(
            f"""select r.id, r.stars, r.text, r.created_on, u.username {common_query} order by r.id desc {limit};"""
        )
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    return JsonResponse({"msg": "success", "data": {"columns": columns, "rows": rows, "count": count}})

