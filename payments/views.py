import base64
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
# from home.email import send_email
from django.contrib.auth.decorators import login_required
import stripe
from django.contrib import messages
import time

from home.models import DiscountCoupon
from .models import CoursePayment, Order
from datetime import date
from post.models import Course
from datetime import datetime
# ----------------- Client's stripe keys -----------------

# ----------------- Developers's stripe keys -----------------
PUBLISHABLE_KEY = 'pk_test_51JI7oJSG0Enolnml5h3Njce3790q5fQ0vtQQWRsB16BE2KphCeyOIzM4TWohFtevid5rvAqlPFBCKUVqHA3oBZNP00yilOjFC6'
SECRET_KEY = 'sk_test_51JI7oJSG0EnolnmlwldUR8NNx4HjY4vlexz6WvdmjJjxAL7GziGfMoaWqSotq9Z6ROxmrNvi7m4X6VvBcDDPFavw00HiQkO2GY'
ENDPOINT_SECRET = 'whsec_zCm1QxzhdwevPm7uPzjzIVlWr9NhL0SQ'
# ----------------- -------------------- -----------------

# stripe settings
stripe.api_key = SECRET_KEY


# Create your views here.
def home(request):
    return HttpResponse("Payment Page")


@login_required
def pay_course(request):
    if request.method != 'POST':
        raise Http404
    course = get_object_or_404(Course, id=request.POST['course_id'])
    price = course.discount_price if course.discount_price else course.price
    if 'coupon_id' in request.POST and request.POST['coupon_id']:
        try:
            if coupon.exp_date < datetime.utcnow().date() or coupon.status == False:
                messages.error(request, 'Coupon expired.')
                return redirect(f'/course/{course.id}/checkout')

            coupon = DiscountCoupon.objects.get(id=request.POST['coupon_id'])
            price = price - (price * (coupon.percent/100))
        except DiscountCoupon.DoesNotExist:
            messages.error(request, 'Invalid Coupon.')
            return redirect(f'/course/{course.id}/checkout')
    order = Order.objects.create(
        user_id=request.user.id, pay_status=0, amount=price, product_type='course', product_id=course.id
    )
    
    pay_time_str = f"{order.id}-{time.time()}"
    pay_time_bytes = pay_time_str.encode("ascii")
    pay_time_base64_bytes = base64.b64encode(pay_time_bytes)
    pay_time_base64_string = pay_time_base64_bytes.decode("ascii")
    code = pay_time_base64_string.replace('=', '0')
    order.code = code

    base_uri = request.scheme + '://' + request.META['HTTP_HOST']
    pr_img = base_uri + course.image.url

    success_url= f"{base_uri}/payments/course/success/{code}"
    cancel_url= f"{base_uri}/payments/course/cancel/{code}"

    return create_checkout_session(order, price, course.title, pr_img, success_url, cancel_url)


def create_checkout_session(order:Order, price, pr_name, pr_img, success_url, cancel_url):
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price_data': {
                        # 'currency': 'usd',
                        'currency': 'inr',
                        'unit_amount': int(price * 100),
                        'product_data': {
                            'name': pr_name,
                            'images': [pr_img]
                        }
                    },
                    'quantity': 1,
                },
            ],
            metadata={"order_id": order.id},
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
        )
        order.stripe_session_id = checkout_session.id
        order.save()
    except Exception as e:
        # return str(e)
        return HttpResponse(str(e))
    # print(vars(checkout_session))
    return redirect(checkout_session.url, code=303)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, ENDPOINT_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Save an order in your database, marked as 'awaiting payment'

        # TestLog.objects.create(data=json.dumps(event['data']))
        mark_success(session)

    elif event['type'] == 'checkout.session.async_payment_succeeded':
        session = event['data']['object']

        # Fulfill the purchase
        mark_success(session)

    elif event['type'] == 'checkout.session.async_payment_failed':
        session = event['data']['object']

        # Send an email to the customer asking them to retry their order
        mark_failed(session)

    elif event['type'] == 'checkout.session.expired':
        session = event['data']['object']

        # Send an email to the customer asking them to retry their order
        mark_expired(session)

    # Passed signature verification
    return HttpResponse(status=200)


def fulfill_order(session):
    # TODO: fill me in
    print("Fulfilling order")


def mark_success(session):
    order = get_object_or_404(Order, id=session.metadata['order_id'])
    order.stripe_session_id = session.id
    if session.payment_status == "paid":
        order.pay_status = 1
    order.payer_email = session['customer_details']['email']
    order.payer_name = session['customer_details']['name']
    order.save()


def mark_failed(session):
    order = get_object_or_404(Order, id=session.metadata['order_id'])
    order.stripe_session_id = session.id
    order.pay_status = 2
    order.payer_email = session['customer_details']['email']
    order.payer_name = session['customer_details']['name']
    order.save()


def mark_expired(session):
    order = get_object_or_404(Order, id=session.metadata['order_id'])
    order.stripe_session_id = session.id
    order.pay_status = 3
    order.payer_email = session['customer_details']['email']
    order.payer_name = session['customer_details']['name']
    order.save()


def course_pay_success(request, code):
    order = get_object_or_404(Order, code=code)
    order.code = None
    order.save()
    if order.pay_status == 1:
        CoursePayment.objects.create(
            user_id=order.user_id,
            course_id=order.product_id,
            order_id=order.id
        )
        messages.success(request, "Payment successful.")
        return redirect('/')
    elif order.pay_status == 0:
        messages.error(request, "Payment Pending.")
        return redirect('/')
    else:
        messages.error(request, "Payment Failed.")
        return redirect('/')



def course_pay_cancel(request, code):
    order = get_object_or_404(Order, code=code)
    order.code = None
    order.save()
    messages.error(request, "Payment cancelled")
    return redirect("/")
