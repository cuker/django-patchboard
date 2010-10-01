from django.dispatch import Signal
import traceback
import sys
from django.core.mail import mail_admins

#our signal
on_error = Signal(providing_args=["exception"])

def handle_error(func, default=None):
    """
    A function decorator that will eat errors
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception, exception:
            on_error.send_robust(sender=None, exception=exception)
            if callable(default):
                return default()
            return default
    return wrapper

def send_failure_email(exception, **kwargs):
    subject = 'Error (%s)' % exception
    subject = subject.replace('\n', '')
    trace = '\n'.join(traceback.format_exception(*sys.exc_info()))

    try:
        mail_admins(subject, trace, fail_silently=True)
    except:
        pass #  TODO

on_error.connect(send_failure_email)
