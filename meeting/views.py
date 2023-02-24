import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from instructor.models import InstructorReview

from student.models import StudentReview
from .models import Appointment, AppointmentModifyReq, AppointmentReview
from django.contrib import messages
from acc.models import User
from utility.helpers import datetime_str_to_utc_datetime_str, time_str_to_utc_time_str, utc_datetime_str_to_datetime_str, utc_time_str_to_time_str
from utility.decorators import user_required


# Create your views here.
@login_required
def book_appointment(request):
    instructor = get_object_or_404(User, id=request.POST['instructor_id'])
    if request.user.time_zone:
        time_zone = request.user.time_zone
        utc_offset = time_zone.utc_offset
        meet_date, start_time = datetime_str_to_utc_datetime_str(
            request.POST['date'], request.POST['start_time'], utc_offset) if request.POST['start_time'] else ''
        end_time = time_str_to_utc_time_str(
            request.POST['end_time'], utc_offset) if request.POST['end_time'] else ''
    else:
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']

    Appointment.objects.create(
        student_id=request.user.id,
        instructor_id=instructor.id,
        start_time=start_time,
        end_time=end_time,
        date=meet_date,
        url=request.POST['url'].strip(),
    )
    messages.success(request, 'Appointment created successfully.')
    return redirect(f'/instructor/{instructor.username}')
    # return HttpResponse("This is test report")


@login_required
def get_appoint_modify_info(request, id):
    appointment = get_object_or_404(Appointment, id=id)
    if appointment.instructor_id != request.user.id and appointment.student_id != request.user.id:
        return JsonResponse({"msg": "Access denied"}, status=401)
    elif not appointment.modify_req:
        return JsonResponse({"msg": "Access denied"}, status=401)
    req = AppointmentModifyReq.objects.filter(appointment_id=id).last()
    if req:
        if request.user.time_zone:
            time_zone = request.user.time_zone
            utc_offset = time_zone.utc_offset
            meet_date, start_time = utc_datetime_str_to_datetime_str(req.date.strftime(
                '%Y-%m-%d'), req.start_time, utc_offset) if req.start_time else ''
            end_time = utc_time_str_to_time_str(
                req.end_time, utc_offset) if req.end_time else ''
        else:
            meet_date = req.date
            start_time = req.start_time
            end_time = req.end_time
        return JsonResponse({
            "msg": "Success",
            "data": {"id": req.id, "date": meet_date, "start_time": start_time, "end_time": end_time, "modify_text": req.modify_text}
        }, status=200)
    else:
        return JsonResponse({"msg": "Modify request not exist."}, status=404)


@user_required
def appointment_rating(request, id):
    user_id = request.user.id
    try:
        appoint = Appointment.objects.get(id=id)
    except Appointment.DoesNotExist:
        return JsonResponse({"msg": "Appointment does not exits."}, status=404)

    if request.method == 'GET':
        if user_id == appoint.instructor_id:
            user_rating = StudentReview.objects.filter(
                student_id=appoint.student_id, user_id=user_id).first()
        elif user_id == appoint.student_id:
            user_rating = InstructorReview.objects.filter(
                instructor_id=appoint.instructor_id, user_id=user_id).first()
        else:
            return JsonResponse({"msg": "Access denied."}, status=401)
        appoint_rating = AppointmentReview.objects.filter(
            appointment_id=appoint.id, user_id=user_id).first()

        return JsonResponse({"msg": "success.", "data": {
            "user_rating": {"id": user_rating.id, "stars": user_rating.stars, "text": user_rating.text} if user_rating else None,
            "appoint_rating": {"id": appoint_rating.id, "stars": appoint_rating.stars, "text": appoint_rating.text} if appoint_rating else None
        }})
    elif request.method == 'POST':
        data = json.loads(request.body)
        if data['type'] == 'user':
            if user_id == appoint.instructor_id:
                user_rating = StudentReview.objects.filter(
                    student_id=appoint.student_id, user_id=user_id).first()
                if user_rating is None:
                    new_rating = StudentReview.objects.create(
                        student_id=appoint.student_id, user_id=user_id, stars=data[
                            'stars'], text=data['text']
                    )
                resource = 'Student’s package rating'
            elif user_id == appoint.student_id:
                user_rating = InstructorReview.objects.filter(
                    instructor_id=appoint.instructor_id, user_id=user_id).first()
                if user_rating is None:
                    new_rating = InstructorReview.objects.create(
                        instructor_id=appoint.instructor_id, user_id=user_id, stars=data[
                            'stars'], text=data['text']
                    )
                resource = 'Instructor’s skills rating'
            else:
                return JsonResponse({"msg": "Access denied."}, status=401)
            if user_rating is None:
                return JsonResponse({
                    "msg": resource + " posted successfully.",
                    "data": {"id": new_rating.id, "stars": new_rating.stars, "text": new_rating.text}
                }, status=201)
            else:
                return JsonResponse({"msg": resource + " already exists."}, status=409)
        elif data['type'] == 'appoint':
            appoint_rating = AppointmentReview.objects.filter(
                appointment_id=appoint.id, user_id=user_id).first()
            if appoint_rating is None:
                new_rating = AppointmentReview.objects.create(
                    appointment_id=appoint.id, user_id=user_id, stars=data['stars'], text=data['text']
                )
                return JsonResponse({
                    "msg": "Appointment rating posted successfully.",
                    "data": {"id": new_rating.id, "stars": new_rating.stars, "text": new_rating.text}
                }, status=201)
            else:
                return JsonResponse({"msg": "Appointment rating already exists."}, status=409)
        else:
            return JsonResponse({"msg": "Bad request."}, status=400)
    else:
        return JsonResponse({"msg": "Method not allowed."}, status=405)


@login_required
def appointment(request, id):
    appoint = get_object_or_404(Appointment, id=id)
    to_user = None
    if appoint.student_id == request.user.id:
        to_user = appoint.instructor_id
    elif appoint.instructor_id == request.user.id:
        to_user = appoint.student_id
    else:
        return HttpResponse("You are not a participant of this appointment.", status=401)
    return render(request, "meeting/appointment.html", {'to_user': to_user})
