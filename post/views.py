import email
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from utility.decorators import user_required, instructor_required, student_required
from django.db import connection
from django.http import JsonResponse, Http404, HttpResponse
from .models import AnsDisapprove, AnsVote, Answer, Like, LookingForMentor, LookingForWork, Question, AnsEndorse, Blog
import json
from post.models import Category
from django.utils.text import slugify
import itertools
import os


# Create your views here.
@user_required
def question(request, id):
    extra_fields = ''
    user_id = request.user.id
    if request.user.role == 3:
        extra_fields = f""", (select count(id) from ans_endorses where answer_id=a.id and user_id={user_id} limit 1) as endorsed,
        (select count(id) from ans_disapproves where answer_id=a.id and user_id={user_id} limit 1) as disapproved"""
    with connection.cursor() as cursor:
        cursor.execute(
            f"""select q.id, q.text, q.created_on, u.username, c.title as category_title,
            (select count(id) from likes where question_id=q.id) as likes,
            (select count(id) from likes where question_id=q.id and user_id={user_id} limit 1) as liked,
            (select count(id) from answers where question_id=q.id) as answers from questions q
            inner join acc_user u on q.user_id=u.id left join categories c on q.category_id=c.id where q.id={id}""")
        ques = cursor.fetchone()
        cursor.execute(
            f"""SELECT a.id, a.text, a.created_on, u.username, (select count(id) from ans_votes where answer_id=a.id) as votes,
            (select count(id) from ans_votes where answer_id=a.id and user_id={user_id} limit 1) as voted,
            (select count(id) from ans_endorses where answer_id=a.id) as endorses,
            (select count(id) from ans_disapproves where answer_id=a.id) as disapproves {extra_fields} from answers a
            inner join acc_user u on a.user_id= u.id where a.question_id = {id} order by votes desc""")
        # columns = [col[0] for col in cursor.description]
        answers = cursor.fetchall()
    return render(request, 'post/question-detail.html', {"answers": answers, "question": ques})


@user_required
def question_list(request):
    condition = 'WHERE true'
    user_id = request.user.id
    if request.GET['category']:
        condition += f" and q.category_id={request.GET['category']}"
    if request.GET['search']:
        condition += f" and (u.username ilike '%{request.GET['search']}%' or q.text ilike '%{request.GET['search']}%')"
    limit = f"OFFSET {request.GET['offset']} LIMIT {request.GET['no_of_row']}"
    with connection.cursor() as cursor:
        cursor.execute(
            f"""SELECT COUNT(q.id) AS count from questions q inner join acc_user u on q.user_id=u.id
            left join categories c on q.category_id=c.id {condition};""")
        count = cursor.fetchone()[0]
        cursor.execute(
            f"""select q.id, q.text, q.created_on, u.username, c.title as category_title,
            (select count(id) from likes where question_id=q.id) as likes,
            (select count(id) from likes where question_id=q.id and user_id={user_id} limit 1) as liked,
            (select count(id) from answers where question_id=q.id) as answers from questions q
            inner join acc_user u on q.user_id=u.id left join categories c on q.category_id=c.id
            {condition} order by q.id desc {limit};"""
        )
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    return JsonResponse({"msg": "success", "data": {"columns": columns, "rows": rows, "count": count}})


@user_required
def my_question_list(request):
    user_id = request.user.id
    condition = f'WHERE q.user_id={user_id}'
    if request.GET['category']:
        condition += f" and q.category_id={request.GET['category']}"
    if request.GET['search']:
        condition += f" and (u.username like '%{request.GET['search']}%' or q.text like '%{request.GET['search']}%')"
    limit = f"OFFSET {request.GET['offset']} LIMIT {request.GET['no_of_row']}"
    with connection.cursor() as cursor:
        cursor.execute(
            f"""SELECT COUNT(q.id) AS count from questions q inner join acc_user u on q.user_id=u.id
            left join categories c on q.category_id=c.id {condition};""")
        count = cursor.fetchone()[0]
        cursor.execute(
            f"""select q.id, q.text, q.created_on, u.username, c.title as category_title,
            (select count(id) from likes where question_id=q.id) as likes,
            (select count(id) from likes where question_id=q.id and user_id={user_id} limit 1) as liked,
            (select count(id) from answers where question_id=q.id) as answers from questions q
            inner join acc_user u on q.user_id=u.id left join categories c on q.category_id=c.id
            {condition} order by q.id desc {limit};"""
        )
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    return JsonResponse({"msg": "success", "data": {"columns": columns, "rows": rows, "count": count}})


@user_required
def like_question(request, id):
    try:
        Question.objects.get(id=id)
    except Question.DoesNotExist:
        return JsonResponse({"msg": "Question does not exist", "data": {}}, status=404)
    try:
        Like.objects.get(question_id=id, user_id=request.user.id)
        return JsonResponse({"msg": "Like already exist", "data": {}}, status=409)
    except Like.DoesNotExist:
        like = Like.objects.create(
            question_id=id,
            user_id=request.user.id
        )
        return JsonResponse({"msg": "success", "data": {"like_id": like.id, }}, status=201)


@user_required
def unlike_question(request, id):
    try:
        Like.objects.get(question_id=id, user_id=request.user.id).delete()
        return JsonResponse({"msg": "success", "data": {}}, status=200)
    except Like.DoesNotExist:
        return JsonResponse({"msg": "Like does not exist", "data": {}}, status=404)


@user_required
def post_question(request):
    if request.method == 'GET':
        cats = Category.objects.filter(status=True).order_by("-id")
        return render(request, 'post/post-question.html', {"categories": cats})
    elif request.method == 'POST':
        Question.objects.create(
            category_id=request.POST['category'],
            text=request.POST['question'],
            user_id=request.user.id
        )
        return redirect('/post/my-questions')
    else:
        raise Http404


def edit_question(request, id):
    try:
        que = Question.objects.get(id=id)
    except Question.DoesNotExist:
        raise Http404
    if request.method == "GET":
        cats = Category.objects.filter(status=True).order_by("-id")
        return render(request, 'post/post-question.html', {"que": que, "categories": cats})
    elif request.method == "POST":
        que.text = request.POST['question']
        que.category_id = request.POST['category']
        que.save()
        return redirect(f"/post/question/{id}/edit")
    else:
        raise Http404


@user_required
def my_questions(request):
    q_list = Question.objects.filter(user_id=request.user.id).order_by("-id")
    return render(request, "post/my-questions.html", {"questions": q_list})


@user_required
def questions(request):
    cats = Category.objects.filter(status=True).order_by("-id")
    return render(request, 'post/questions.html', {'categories': cats})


@user_required
def answer_create(request, id):
    if request.method == 'POST':
        try:
            Question.objects.get(id=id)
            Answer.objects.create(
                question_id=id,
                user_id=request.user.id,
                text=request.POST['answer'],
            )
        except Question.DoesNotExist:
            return JsonResponse({"msg": "Question does not exist", "data": {}}, status=404)
        return redirect('/post/question/'+str(id))
    else:
        raise Http404


def edit_answer(request, id):
    try:
        ans = Answer.objects.get(id=id)
    except Answer.DoesNotExist:
        raise Http404
    if request.method == "GET":
        return render(request, 'post/edit-answer.html', {"ans": ans, })
    elif request.method == "POST":
        ans.text = request.POST['answer']
        ans.save()
        return redirect(f"/post/answer/{id}/edit")
    else:
        raise Http404


@user_required
def vote_answer(request, id):
    try:
        Answer.objects.get(id=id)
    except Answer.DoesNotExist:
        return JsonResponse({"msg": "Answer does not exist", "data": {}}, status=404)
    try:
        AnsVote.objects.get(answer_id=id, user_id=request.user.id)
        return JsonResponse({"msg": "Answer already exist", "data": {}}, status=409)
    except AnsVote.DoesNotExist:
        vote = AnsVote.objects.create(
            answer_id=id,
            user_id=request.user.id
        )
        return JsonResponse({"msg": "success", "data": {"vote_id": vote.id}}, status=201)


@user_required
def unvote_answer(request, id):
    try:
        AnsVote.objects.get(answer_id=id, user_id=request.user.id).delete()
        return JsonResponse({"msg": "success", "data": {}}, status=200)
    except AnsVote.DoesNotExist:
        return JsonResponse({"msg": "Vote does not exist", "data": {}}, status=404)


@user_required
def endorse_answer(request, id):
    if request.user.role != 3:
        return JsonResponse({"msg": "Access denied", "data": {}}, status=401)
    try:
        Answer.objects.get(id=id)
    except Answer.DoesNotExist:
        return JsonResponse({"msg": "Answer does not exist", "data": {}}, status=404)
    try:
        AnsEndorse.objects.get(answer_id=id, user_id=request.user.id)
        return JsonResponse({"msg": "Endorse already exist", "data": {}}, status=409)
    except AnsEndorse.DoesNotExist:
        endorse = AnsEndorse.objects.create(
            answer_id=id,
            user_id=request.user.id
        )
        return JsonResponse({"msg": "success", "data": {"endorse_id": endorse.id}}, status=201)


@user_required
def unendorse_answer(request, id):
    if request.user.role != 3:
        return JsonResponse({"msg": "Access denied", "data": {}}, status=401)
    try:
        AnsEndorse.objects.get(answer_id=id, user_id=request.user.id).delete()
        return JsonResponse({"msg": "success", "data": {}}, status=200)
    except AnsEndorse.DoesNotExist:
        return JsonResponse({"msg": "Endorse does not exist", "data": {}}, status=404)


@user_required
def disapprove_answer(request, id):
    if request.user.role != 3:
        return JsonResponse({"msg": "Access denied", "data": {}}, status=401)
    try:
        Answer.objects.get(id=id)
    except Answer.DoesNotExist:
        return JsonResponse({"msg": "Answer does not exist", "data": {}}, status=404)
    try:
        AnsDisapprove.objects.get(answer_id=id, user_id=request.user.id)
        return JsonResponse({"msg": "Disapprove already exist", "data": {}}, status=409)
    except AnsDisapprove.DoesNotExist:
        disapprove = AnsDisapprove.objects.create(
            answer_id=id,
            user_id=request.user.id
        )
        return JsonResponse({"msg": "success", "data": {"disapprove_id": disapprove.id}}, status=201)


@user_required
def undisapprove_answer(request, id):
    if request.user.role != 3:
        return JsonResponse({"msg": "Access denied", "data": {}}, status=401)
    try:
        AnsDisapprove.objects.get(
            answer_id=id, user_id=request.user.id).delete()
        return JsonResponse({"msg": "success", "data": {}}, status=200)
    except AnsDisapprove.DoesNotExist:
        return JsonResponse({"msg": "Disapprove does not exist", "data": {}}, status=404)


@user_required
def blog_create(request):
    if request.method == "GET":
        return render(request, "post/post-blog.html")
    elif request.method == 'POST':
        # ---------- generating slug ----------
        slug_candidate = slug_original = slugify(request.POST['title'])
        for i in itertools.count(1):
            if not Blog.objects.filter(slug=slug_candidate).exists():
                break
            slug_candidate = '{}-{}'.format(slug_original, i)
        # -------------------------------------
        Blog.objects.create(
            title=request.POST['title'],
            about=request.POST['about'],
            slug=slug_candidate,
            video=request.FILES['video'] if 'video' in request.FILES else None,
            image=request.FILES['image'] if 'image' in request.FILES else None,
            body=request.POST['body'],
            user_id=request.user.id
        )
        return redirect('/post/blog/create')
    else:
        raise Http404


@user_required
def blog_edit(request, id):
    try:
        blog = Blog.objects.get(id=id)
        if blog.user_id != request.user.id:
            return HttpResponse('Access Denied', status=403)
    except Blog.DoesNotExist:
        raise Http404
    if request.method == "GET":
        return render(request, "post/post-blog.html", {'blog': blog})
    elif request.method == 'POST':
        if 'image' in request.FILES:
            if blog.image:
                os.remove(blog.image.path)
            blog.image = request.FILES['image']
        if 'video' in request.FILES:
            if blog.video:
                os.remove(blog.video.path)
            blog.video = request.FILES['video']
        blog.title = request.POST['title']
        blog.about = request.POST['about']
        blog.body = request.POST['body']
        blog.save()
        return redirect('/post/blog/create')
    else:
        raise Http404


@user_required
def looking_for_mentor(request):
    return render(request, "post/looking-for-mentor.html")


@user_required
def looking_for_mentor_list(request):
    limit = f"OFFSET {request.GET['offset']} LIMIT {request.GET['no_of_row']}"
    with connection.cursor() as cursor:
        com_query = 'from looking_for_mentors lk inner join acc_user u on lk.user_id=u.id'
        cursor.execute(f"SELECT COUNT(lk.id) AS count {com_query};")
        count = cursor.fetchone()[0]
        cursor.execute(
            f"""select lk.id, lk.user_id, u.username, lk.title, lk.text, lk.created_on {com_query}
            order by lk.id desc {limit};"""
        )
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    return JsonResponse({"msg": "success", "data": {"columns": columns, "rows": rows, "count": count}})


@student_required
def post_looking_for_mentor(request):
    if request.method == 'GET':
        return render(request, "post/post-looking-for-mentor.html")
    elif request.method == 'POST':
        LookingForMentor.objects.create(
            title=request.POST['title'],
            text=request.POST['text'],
            user_id=request.user.id
        )
        return redirect('/post/looking-for-mentor')
    else:
        raise Http404


@user_required
def looking_for_work(request):
    return render(request, "post/looking-for-work.html")


@user_required
def looking_for_work_list(request):
    limit = f"OFFSET {request.GET['offset']} LIMIT {request.GET['no_of_row']}"
    with connection.cursor() as cursor:
        com_query = 'from looking_for_works lk inner join acc_user u on lk.user_id=u.id'
        cursor.execute(f"SELECT COUNT(lk.id) AS count {com_query};")
        count = cursor.fetchone()[0]
        cursor.execute(
            f"""select lk.id, lk.user_id, u.username, lk.title, lk.text, lk.created_on {com_query}
            order by lk.id desc {limit};"""
        )
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    return JsonResponse({"msg": "success", "data": {"columns": columns, "rows": rows, "count": count}})


@instructor_required
def post_looking_for_work(request):
    if request.method == 'GET':
        return render(request, "post/post-looking-for-work.html")
    elif request.method == 'POST':
        LookingForWork.objects.create(
            title=request.POST['title'],
            text=request.POST['text'],
            user_id=request.user.id
        )
        return redirect('/post/looking-for-work')
    else:
        raise Http404

