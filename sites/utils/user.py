from django.core.mail import send_mail
from hydroserver.settings import PROXY_BASE_URL
from django.template.loader import render_to_string

def user_to_dict(user):
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "middle_name": user.middle_name,
        "last_name": user.last_name,
        "phone": user.phone,
        "address": user.address,
        "organization": user.organization,
        "type": user.type
    }

def send_password_reset_email(user, uid, token):
    mail_subject = 'Password Reset'

    context = {
        'user': user,
        'uid': uid,
        'token': token,
        'domain': 'hydroserver.ciroh.org',  
        'proxy_base_url': PROXY_BASE_URL
    }

    html_message = render_to_string('reset_password_email.html', context)

    send_mail(
        mail_subject,
        '', # Don't support plain text emails
        'HydroServer <admin@hydroserver.ciroh.org>',
        [user.email],
        html_message=html_message,
    )