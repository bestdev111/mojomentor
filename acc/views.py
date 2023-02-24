from django.shortcuts import render, redirect
from acc.models import ChatUser, User
from utility.helpers import gen_link_token, verify_link_token
from utility.emails import send_html_email
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from utility.zoom import gen_zoom_sdk_jwt, create_zoom_meeting, create_zoom_user
from django.db import connection
import json
from django.core.files.base import ContentFile
import base64
from django.contrib import messages
from acc.models import Follower
from utility.decorators import admin_required, user_required
from django.core.files.storage import FileSystemStorage
from time import time
import os

# Create your views here.

@login_required
def send_email_confirmation_link(request):
    link = f"{request.scheme}://{request.META['HTTP_HOST']}/account/confirm-email/{gen_link_token(request.user)}"
    html_body = render_to_string(
        'emails/confirm-email.html', {'link': link}
    )
    result = send_html_email(
        'Email confirmation', html_body, request.user.email
    )
    if result:
        return JsonResponse({"msg": "Email confirmation link sent"}, status=201)
    else:
        return JsonResponse({"msg": "Email confirmation link sending failed"}, status=500)


@login_required
def confirm_email(request, token):
    if request.method == 'GET':
        return render(request, 'acc/confirm-email.html')
    elif request.method == 'POST':
        code, msg = verify_link_token(token)
        if code == 200:
            request.user.email_verified = True
            request.user.save()
        return JsonResponse({"msg": msg}, status=code)
    else:
        return JsonResponse({"msg": "Method not allowed"}, status=405)


@login_required
def chats(request):
    with connection.cursor() as cursor:
        cursor.execute(
            f"""SELECT u.id AS user_id, u.username, u.profile_pic FROM acc_user u
            INNER JOIN (SELECT id, user1_id AS person_id FROM chat_users
            WHERE user2_id = {request.user.id} UNION ALL SELECT id, user2_id AS person_id
            FROM chat_users WHERE user1_id = {request.user.id}) cu ON u.id = cu.person_id;"""
        )
        # columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    return render(request, 'acc/chats.html', {'users': rows})


@login_required
def create_chat_user(request, id):
    ChatUser.objects.create(user1_id=request.user.id, user2_id=id)
    return redirect('/account/chats')


@login_required
def test_url(request):
    zoom_role = 1 if request.user.role == 3 else 0
    meeting_no = 8
    signature = gen_zoom_sdk_jwt(zoom_role, meeting_no)
    # create_zoom_user()
    create_zoom_meeting()
    # url = f'/account/meeting?name=sonu&role={zoom_role}&mn={meeting_no}&lang=en-US&signature={signature}'
    return HttpResponse("Hello")  # render(request, 'acc/zoom.html')
    # return redirect(url)


def meeting(request):
    return render(request, 'acc/meeting.html')


@login_required
def update(request):
    if request.method != 'POST':
        return JsonResponse({'msg': 'Method not allowed'}, status=405)
    data = json.loads(request.body)
    user = request.user
    if data['type'] == 'basic_info':
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.phone_no = data['phone_no']
        if data['location']:
            user.country_id = data['location']
        if data['time_zone']:
            user.time_zone_id = data['time_zone']

    elif data['type'] == 'pic':
        format, imgstr = data["pic_data"].split(';base64,')
        ext = format.split('/')[-1]
        name = f"user-{request.user.id}-{str(time()).replace('.', '_')}.{ext}"
        image = ContentFile(base64.b64decode(imgstr), name=name)

        if user.profile_pic and os.path.isfile(user.profile_pic.path):
            os.remove(user.profile_pic.path)
        user.profile_pic = image

    elif data['type'] == 'email':
        email = data["email"].strip()
        try:
            User.objects.get(email=email)
            return JsonResponse({'msg': 'Email already exist'}, status=409)
        except User.DoesNotExist:
            user.email = email
            user.email_verified = False

    elif data['type'] == 'password':
        if user.check_password(data["password"]):
            user.set_password(data['new_password'])
        else:
            return JsonResponse({'msg': 'Incorrect password'}, status=401)

    user.save()
    return JsonResponse({'msg': 'Information updated successfully'}, status=200)


@login_required
def get_chats(request, user_id):
    with connection.cursor() as cursor:
        cursor.execute(
            f"""SELECT CASE WHEN user1_id = {user_id} THEN 'receive' ELSE 'send' END flow, type, msg,
            created_on FROM chats WHERE (user1_id = {request.user.id} AND user2_id = {user_id}) OR
            (user1_id = {user_id} AND user2_id = {request.user.id})"""
        )
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    return JsonResponse({'msg': 'success', 'data': {'rows': rows, 'columns': columns}}, status=200)


@admin_required
def change_status(request, id):
    data = json.loads(request.body)
    try:
        user = User.objects.get(id=id)
        if data['status'] == 1:
            user.is_active = True
        else:
            user.is_active = False
        user.save()
        messages.success(request, 'Status changed successfully')
        return JsonResponse({'msg': 'Status changed successfully'}, status=200)
    except User.DoesNotExist:
        return JsonResponse({'msg': 'User does not exist.'}, status=404)


@login_required
def follow_user(request, id):
    try:
        User.objects.get(id=id)
    except User.DoesNotExist:
        return JsonResponse({"msg": "User does not exist", "data": {}}, status=404)
    try:
        Follower.objects.get(to_user_id=id, from_user_id=request.user.id)
        return JsonResponse({"msg": "Follower already exist", "data": {}}, status=409)
    except Follower.DoesNotExist:
        follower = Follower.objects.create(
            to_user_id=id,
            from_user_id=request.user.id
        )
        return JsonResponse({"msg": "success", "data": {"follower_id": follower.id, }}, status=201)


@login_required
def unfollow_user(request, id):
    try:
        Follower.objects.get(to_user_id=id, from_user_id=request.user.id).delete()
        return JsonResponse({"msg": "success", "data": {}}, status=200)
    except Follower.DoesNotExist:
        return JsonResponse({"msg": "Follower does not exist", "data": {}}, status=404)


@user_required
def my_referrals(request):
    refer_url = f"{request.scheme}://{request.META['HTTP_HOST']}/register?refer_by={request.user.username}"
    return render(request, 'acc/my-referrals.html', {'refer_url': refer_url})


@user_required
def my_referrals_list(request):
    with connection.cursor() as cursor:
        limit = f"OFFSET {request.GET['offset']} LIMIT {request.GET['no_of_row']}"
        common_query = f"FROM referrals rf INNER JOIN acc_user u ON rf.refer_to_id=u.id WHERE rf.refer_by_id={request.user.id}"
        cursor.execute(f"SELECT COUNT(rf.id) AS count {common_query}")
        count = cursor.fetchone()[0]
        cursor.execute(
            f"SELECT rf.id, u.username, rf.created_on {common_query} ORDER BY id DESC {limit}"
        )
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    return JsonResponse({"msg": "success", "data": {"columns": columns, "rows": rows, "count": count}})


@user_required
def chat_file_upload(request):
    f = request.FILES['file']
    file_path = f"chat-files/user-{request.user.id}/{str(time()).replace('.', '_')}.{f.name.split('.')[-1]}"
    FileSystemStorage().save(file_path, f)
    return JsonResponse({"msg": "success", "data": {"file_path": file_path}})