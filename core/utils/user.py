from django.core.mail import send_mail
from hydroserver.settings import PROXY_BASE_URL
from django.template.loader import render_to_string
from core.utils.organization import organization_to_dict

def user_to_dict(user):
    return {
        "id": user.id,
        "email": user.email,
        "firstName": user.first_name,
        "middleName": user.middle_name,
        "lastName": user.last_name,
        "phone": user.phone,
        "address": user.address,
        "isVerified": user.is_verified,
        "organization": organization_to_dict(user.organization) if user.organization else None,
        "type": user.type, 
        "link": user.link
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
        '',  # Don't support plain text emails
        'HydroServer <admin@hydroserver.ciroh.org>',
        [user.email],
        html_message=html_message,
    )
