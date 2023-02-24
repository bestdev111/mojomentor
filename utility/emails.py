from django.conf import settings
from django.core.mail import EmailMessage, send_mail


def send_email(subject, body, email):
    try:
        email_msg = EmailMessage(
            subject, body, settings.EMAIL_HOST_USER, [email],
        )
        email_msg.send()
        return True
    except:
        return False


def send_html_email(subject, html_body, email):
    try:
        send_mail(
            subject, '', settings.EMAIL_HOST_USER, [email], html_message=html_body
        )
        return True
    except:
        return False
