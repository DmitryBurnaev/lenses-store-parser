# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.core.mail import send_mail

log = logging.getLogger(__name__)


def system_notification(message):
    log.warning(message)
    send_mail(
        '[lensgo-parsing] Системное уведомление',
        message,
        settings.DEFAULT_FROM_EMAIL,
        dict(settings.ADMINS).values()
    )

