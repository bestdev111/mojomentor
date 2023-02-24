from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import get_object_or_404, render, redirect
from admin_panel.models import Setting
from post.models import Category
from utility.decorators import admin_required, super_admin_required
from django.db import connection
from django.contrib import messages
from home.models import DiscountCoupon, Faq
from acc.models import User
import json
from django.contrib.auth import login


# Create your views here.
@admin_required
def index(request):
    return redirect('/admin/dashboard')


@admin_required
def dashboard(request):
    return render(request, 'admin/ad-dashboard.html')


def auth_login(request):
    if request.method == "GET":
        return render(request, 'admin/ad-login.html')

    elif request.method == "POST":
        data = json.loads(request.body)
        email = data["email"].strip()
        try:
            user = User.objects.get(email=email)
            if user.role != 1 and user.role != 2:
                return JsonResponse({"massage": "You not have any admin account."}, status=401)
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


# ------------------------ categories ------------------------
@admin_required
def categories(request):
    return render(request, 'admin/ad-categories.html')


@admin_required
def category_list(request):
    condition = 'WHERE true'
    user_id = request.user.id
    # if request.GET['category']:
    #     condition += f" and q.category_id={request.GET['category']}"
    if request.GET['search']:
        condition += f" and (title ilike '%{request.GET['search']}%')"
    limit = f"OFFSET {request.GET['offset']} LIMIT {request.GET['no_of_row']}"
    with connection.cursor() as cursor:
        cursor.execute(
            f"""SELECT COUNT(id) AS count from categories {condition};""")
        count = cursor.fetchone()[0]
        cursor.execute(
            f"""select id, title, status, created_on from categories {condition} order by id desc {limit};"""
        )
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    return JsonResponse({"msg": "success", "data": {"columns": columns, "rows": rows, "status": 2, "count": count, "date_times": [3]}})


@admin_required
def edit_category(request, id):
    category = get_object_or_404(Category, id=id)
    if request.method == 'GET':
        print(category.status)
        return render(request, 'admin/ad-category-form.html', {'category': category})
    elif request.method == 'POST':
        category.status = True if request.POST['status'] == '1' else False
        category.save()
        messages.success(request, 'Category saved successfully.')
        return redirect('/admin/categories')
    else:
        return HttpResponse("Method not allowed", status=405)


@admin_required
def create_category(request):
    if request.method == 'GET':
        return render(request, 'admin/ad-category-form.html')
    elif request.method == 'POST':
        Category.objects.create(
            title=request.POST['title'],
            status=True if request.POST['status'] == '1' else False
        )
        messages.success(request, 'Category saved successfully.')
        return redirect('/admin/categories')
    else:
        return HttpResponse("Method not allowed", status=405)


# ------------------------ coupons ------------------------
@admin_required
def coupons(request):
    return render(request, 'admin/ad-coupons.html')


@admin_required
def coupon_list(request):
    condition = 'WHERE true'
    user_id = request.user.id
    # if request.GET['category']:
    #     condition += f" and q.category_id={request.GET['category']}"
    if request.GET['search']:
        condition += f" and (code ilike '%{request.GET['search']}%')"
    limit = f"OFFSET {request.GET['offset']} LIMIT {request.GET['no_of_row']}"
    with connection.cursor() as cursor:
        cursor.execute(
            f"""SELECT COUNT(id) AS count from discount_coupons {condition};""")
        count = cursor.fetchone()[0]
        cursor.execute(
            f"""select id, code, percent, status, created_on from discount_coupons {condition} order by id desc {limit};"""
        )
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    return JsonResponse({"msg": "success", "data": {"columns": columns, "rows": rows, "status": 3, "count": count, "date_times": [4]}})


@admin_required
def edit_coupon(request, id):
    coupon = get_object_or_404(DiscountCoupon, id=id)
    if request.method == 'GET':
        print(coupon.status)
        return render(request, 'admin/ad-coupon-form.html', {'coupon': coupon})
    elif request.method == 'POST':
        coupon.code = request.POST['code'].upper()
        coupon.percent = request.POST['percent']
        coupon.exp_date = request.POST['exp_date']
        coupon.status = True if request.POST['status'] == '1' else False
        coupon.save()
        messages.success(request, 'coupon saved successfully.')
        return redirect('/admin/coupons')
    else:
        return HttpResponse("Method not allowed", status=405)


@admin_required
def create_coupon(request):
    if request.method == 'GET':
        return render(request, 'admin/ad-coupon-form.html')
    elif request.method == 'POST':
        DiscountCoupon.objects.create(
            code=request.POST['code'].upper(),
            percent=request.POST['percent'],
            exp_date=request.POST['exp_date'],
            status=True if request.POST['status'] == '1' else False
        )
        messages.success(request, 'coupon saved successfully.')
        return redirect('/admin/coupons')
    else:
        return HttpResponse("Method not allowed", status=405)


@admin_required
def delete_coupon(request, id):
    coupon = get_object_or_404(DiscountCoupon, id=id)
    coupon.delete()
    return JsonResponse({"msg": "success", "data": {}}, status=200)


# ------------------------ student/user ------------------------
@admin_required
def students(request):
    return render(request, 'admin/ad-students.html')


@admin_required
def student_list(request):
    condition = 'WHERE true'
    user_id = request.user.id
    # if request.GET['category']:
    #     condition += f" and q.category_id={request.GET['category']}"
    if request.GET['search']:
        condition += f" and (username ilike '%{request.GET['search']}%' or email ilike '%{request.GET['search']}%' or first_name ilike '%{request.GET['search']}%' or last_name ilike '%{request.GET['search']}%')"
    limit = f"OFFSET {request.GET['offset']} LIMIT {request.GET['no_of_row']}"
    condition += ' AND role=4 '
    with connection.cursor() as cursor:
        cursor.execute(
            f"""SELECT COUNT(id) AS count from acc_user {condition};""")
        count = cursor.fetchone()[0]
        cursor.execute(
            f"""select id, username, first_name, last_name, email, is_active AS status, date_joined from acc_user {condition} order by id desc {limit};"""
        )
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    return JsonResponse({"msg": "success", "data": {"columns": columns, "rows": rows, "status": 5, "count": count, "date_times": [6]}})


@admin_required
def view_student(request, id):
    user = get_object_or_404(User, id=id)
    return render(request, 'admin/ad-student-form.html', {"student": user})

@admin_required
def user_chats(request, id):
    curr_user_obj = get_object_or_404(User, id=id)
    with connection.cursor() as cursor:
        cursor.execute(
            f"""SELECT u.id AS user_id, u.username, u.profile_pic FROM acc_user u
            INNER JOIN (SELECT id, user1_id AS person_id FROM chat_users
            WHERE user2_id = {id} UNION ALL SELECT id, user2_id AS person_id
            FROM chat_users WHERE user1_id = {id}) cu ON u.id = cu.person_id;"""
        )
        # columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    return render(request, 'admin/ad-user-chats.html', {'users': rows, 'curr_user': id, 'curr_user_obj': curr_user_obj})

@admin_required
def user_get_chats(request , curr_id, to_id):
    with connection.cursor() as cursor:
        cursor.execute(
            f"""SELECT CASE WHEN user1_id = {to_id} THEN 'receive' ELSE 'send' END flow, type, msg,
            created_on FROM chats WHERE (user1_id = {curr_id} AND user2_id = {to_id}) OR
            (user1_id = {to_id} AND user2_id = {curr_id})"""
        )
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    return JsonResponse({'msg': 'success', 'data': {'rows': rows, 'columns': columns}}, status=200)


# ------------------------ instructor/user ------------------------
@admin_required
def instructors(request):
    return render(request, 'admin/ad-instructors.html')


@admin_required
def instructor_list(request):
    condition = 'WHERE true'
    user_id = request.user.id
    # if request.GET['category']:
    #     condition += f" and q.category_id={request.GET['category']}"
    if request.GET['search']:
        condition += f" and (username ilike '%{request.GET['search']}%' or email ilike '%{request.GET['search']}%' or first_name ilike '%{request.GET['search']}%' or last_name ilike '%{request.GET['search']}%')"
    limit = f"OFFSET {request.GET['offset']} LIMIT {request.GET['no_of_row']}"
    condition += ' AND role=3 '
    with connection.cursor() as cursor:
        cursor.execute(
            f"""SELECT COUNT(id) AS count from acc_user {condition};""")
        count = cursor.fetchone()[0]
        cursor.execute(
            f"""select id, username, first_name, last_name, email, is_active AS status, date_joined from acc_user {condition} order by id desc {limit};"""
        )
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    return JsonResponse({"msg": "success", "data": {"columns": columns, "rows": rows, "status": 5, "count": count, "date_times": [6]}})


@admin_required
def view_instructor(request, id):
    user = get_object_or_404(User, id=id)
    return render(request, 'admin/ad-instructor-form.html', {"instructor": user})



# ------------------------ faqs ------------------------
@admin_required
def faqs(request):
    return render(request, 'admin/ad-faqs.html')


@admin_required
def faq_list(request):
    condition = 'WHERE true'
    user_id = request.user.id
    # if request.GET['category']:
    #     condition += f" and q.category_id={request.GET['category']}"
    if request.GET['search']:
        condition += f" and (ques ilike '%{request.GET['search']}%')"
    limit = f"OFFSET {request.GET['offset']} LIMIT {request.GET['no_of_row']}"
    with connection.cursor() as cursor:
        cursor.execute(
            f"""SELECT COUNT(id) AS count from faqs {condition};""")
        count = cursor.fetchone()[0]
        cursor.execute(
            f"""select id, ques AS question, status, created_on from faqs {condition} order by id desc {limit};"""
        )
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    return JsonResponse({"msg": "success", "data": {"columns": columns, "rows": rows, "status": 2, "count": count, "date_times": [3]}})


@admin_required
def edit_faq(request, id):
    faq = get_object_or_404(Faq, id=id)
    if request.method == 'GET':
        return render(request, 'admin/ad-faq-form.html', {'faq': faq})
    elif request.method == 'POST':
        faq.ques = request.POST['ques']
        faq.ans = request.POST['ans']
        faq.status = True if request.POST['status'] == '1' else False
        faq.save()
        messages.success(request, 'FAQ saved successfully.')
        return redirect('/admin/faqs')
    else:
        return HttpResponse("Method not allowed", status=405)


@admin_required
def create_faq(request):
    if request.method == 'GET':
        return render(request, 'admin/ad-faq-form.html')
    elif request.method == 'POST':
        Faq.objects.create(
            ques=request.POST['ques'],
            ans=request.POST['ans'],
            status=True if request.POST['status'] == '1' else False
        )
        messages.success(request, 'FAQ saved successfully.')
        return redirect('/admin/faqs')
    else:
        return HttpResponse("Method not allowed", status=405)


@admin_required
def delete_faq(request, id):
    faq = get_object_or_404(Faq, id=id)
    faq.delete()
    return JsonResponse({"msg": "success", "data": {}}, status=200)


# ------------------------ settings ------------------------
@super_admin_required
def settings(request):
    if request.method == 'GET':
        keys = "'PERCENTAGE'"
        with connection.cursor() as cursor:
            cursor.execute(
                f"""select id, key, value from settings where key in({keys});"""
            )
            # columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
        all_settings = {}
        for row in rows:
            all_settings[row[1]] = row[2]
        return render(request, 'admin/ad-settings.html', {'settings': all_settings})
    elif request.method == 'POST':
        data = json.loads(request.body)
        if data['key'] and data['value']:
            try:
                setting = Setting.objects.get(key=data['key'])
                setting.value = data['value']
                setting.save()
            except Setting.DoesNotExist:
                Setting.objects.create(key=data['key'], value=data['value'])
            return JsonResponse({"msg": "Information saved successfully", "data": {}}, status=200)
        else:
            return JsonResponse({"msg": "Information missing", "data": {}}, status=400)
    else:
        raise Http404
