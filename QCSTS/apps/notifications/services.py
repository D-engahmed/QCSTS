from django.core.mail import send_mail
from django.conf import settings

from .models import Notification


def create_notification(*, user, organization, title, body, kind=Notification.Kind.SYSTEM,
                        severity=Notification.Severity.INFO, action_url="", send_email=True):
    record = Notification.objects.create(
        organization=organization,
        user=user,
        title=title,
        body=body,
        kind=kind,
        severity=severity,
        action_url=action_url,
    )
    if send_email:
        send_mail(
            subject=title,
            message=body,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@qcsts.local"),
            recipient_list=[user.email],
            fail_silently=True,
        )
    return record
