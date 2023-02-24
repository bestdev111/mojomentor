import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from meeting.models import Appointment, AppointmentModifyReq
# from django.http import HttpResponse, JsonResponse
from utility.decorators import student_required
from django.db import connection

from utility.helpers import utc_datetime_str_to_datetime_str, utc_time_str_to_time_str


# Create your views here.
@student_required
def index(request):
    return redirect('/')


@student_required
def dashboard(request):
    return render(request, 'student/stu-dashboard.html')


@student_required
def profile(request):
    with connection.cursor() as cursor:
        cursor.execute(f"select id, name from countries")
        countries = cursor.fetchall()
        cursor.execute(f"select id, name, utc_offset from time_zones")
        time_zones = cursor.fetchall()
    time_zone_id = request.user.time_zone_id if request.user.time_zone_id else 47
    return render(request, 'student/stu-profile.html', {
        'countries': countries, 'time_zones': time_zones, 'time_zone_id': time_zone_id
    })


@student_required
def appointments(request):
    return render(request, 'student/stu-appointments.html')


@student_required
def appointment_list(request):
    with connection.cursor() as cursor:
        limit = f"OFFSET {request.GET['offset']} LIMIT {request.GET['no_of_row']}"
        common_query = f"FROM appointments ap INNER JOIN acc_user u ON ap.instructor_id=u.id WHERE ap.student_id={request.user.id}"
        cursor.execute(f"SELECT COUNT(ap.id) AS count {common_query}")
        count = cursor.fetchone()[0]
        cursor.execute(
            f"""SELECT ap.id, ap.date, ap.start_time, ap.end_time, ap.url, ap.instructor_id,
            u.username, ap.status, ap.modify_req {common_query}
            ORDER BY id DESC {limit}"""
        )
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    return JsonResponse({"msg": "success", "data": {"columns": columns, "rows": rows, "count": count}})


@student_required
def update_appointment(request):
    data = json.loads(request.body)
    appointmentModifyReq = get_object_or_404(AppointmentModifyReq, id=data['modify_id'])
    appointment = appointmentModifyReq.appointment
    if appointment.student_id != request.user.id or appointment.status != 0 or not appointment.modify_req:
        return JsonResponse({"msg": "Access denied"} , status=401)
    msg = 'Success'
    res_data = {}
    if data['type'] == 'accept':
        appointment.status = 1
        msg = 'Appointment accepted successfully.'
        appointment.date = appointmentModifyReq.date
        appointment.start_time = appointmentModifyReq.start_time
        appointment.end_time = appointmentModifyReq.end_time

        if request.user.time_zone:
            time_zone = request.user.time_zone
            utc_offset = time_zone.utc_offset
            res_data["date"], res_data["start_time"] = utc_datetime_str_to_datetime_str(appointment.date.strftime('%Y-%m-%d'), appointment.start_time, utc_offset) if appointment.start_time else ''
            res_data["end_time"] = utc_time_str_to_time_str(appointment.end_time, utc_offset) if appointment.end_time else ''
        else:
            res_data["date"] = appointment.date
            res_data["start_time"] = appointment.start_time
            res_data["end_time"] = appointment.end_time

    elif data['type'] == 'decline':
        appointment.status = 2
        msg = 'Appointment declined successfully.'
    appointment.modify_req = False
    appointment.save()

    res_data["status"] = appointment.status
    res_data["id"] = appointment.id
    res_data["modify_req"] = appointment.modify_req

    return JsonResponse({"msg": msg,"data": res_data}, status=200)


@student_required
def courses(request):
    return render(request, 'student/stu-courses.html')

@student_required
def course_list(request):
    with connection.cursor() as cursor:
        limit = f"OFFSET {request.GET['offset']} LIMIT {request.GET['no_of_row']}"
        common_query = f"FROM course_payments cp LEFT JOIN courses c ON cp.course_id=c.id LEFT JOIN categories ct ON c.category_id = ct.id WHERE cp.user_id={request.user.id}"
        cursor.execute(f"SELECT COUNT(cp.id) AS count {common_query}")
        count = cursor.fetchone()[0]
        cursor.execute(
            f"""SELECT cp.id, cp.course_id, c.title, ct.title as cat_title, cp.created_on {common_query}
            ORDER BY id DESC {limit}"""
        )
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    return JsonResponse({"msg": "success", "data": {"columns": columns, "rows": rows, "count": count}})
