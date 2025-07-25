from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from user_agents import parse
from .models import LoginActivity
from .utils import get_client_info

@receiver(user_logged_in)
def log_login_activity(sender, request, user, **kwargs):
    user_agent_str = request.META.get('HTTP_USER_AGENT', '')
    user_agent = parse(user_agent_str)

    ip = get_client_ip(request)
    browser = f"{user_agent.browser.family} {user_agent.browser.version_string}"
    os = f"{user_agent.os.family} {user_agent.os.version_string}"

    # Block login if more than 3 devices used
    existing_devices = LoginActivity.objects.filter(user=user)
    is_existing_device = existing_devices.filter(
        ip_address=ip,
        browser=browser,
        os=os
    ).exists()

    if not is_existing_device and existing_devices.count() >= 3:
        request.session['login_block_reason'] = "Login blocked: maximum 3 devices allowed per user."
        raise PermissionDenied("Too many active devices.")

    # Save login activity
    LoginActivity.objects.update_or_create(
    user=user,
    ip_address=ip,
    browser=browser,
    os=os
    )


    # Optionally update user fields
    user.browser = browser
    user.os = os
    user.ip_address = ip
    user.save()
@receiver(user_logged_in)
def restrict_multiple_devices(sender, request, user, **kwargs):
    user_agent = parse(request.META.get('HTTP_USER_AGENT', ''))
    ip = get_client_ip(request)
    browser = user_agent.browser.family
    os = user_agent.os.family

    # Check if this device is already logged
    existing_devices = LoginActivity.objects.filter(user=user)
    is_known = existing_devices.filter(ip_address=ip, browser=browser, os=os).exists()

    if not is_known:
        if existing_devices.count() >= 3:
            request.session['login_block_reason'] = "You are logged in on 3 devices. Logout from one to continue."
            raise PermissionDenied("Too many active devices.")

        # Log this new device
        LoginActivity.objects.create(user=user, ip_address=ip, browser=browser, os=os)

def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0]
    return request.META.get('REMOTE_ADDR')



# from django.contrib.auth.signals import user_logged_in
# from django.dispatch import receiver
# from django.utils import timezone
# from django.core.exceptions import PermissionDenied
# from user_agents import parse
# from .models import LoginActivity
# import logging

# @receiver(user_logged_in)
# def handle_login_tracking(sender, request, user, **kwargs):
#     user_agent_str = request.META.get('HTTP_USER_AGENT', '')
#     user_agent = parse(user_agent_str)
#     ip = get_client_ip(request)

#     browser = user_agent.browser.family
#     os = user_agent.os.family

#     # Check if current device/IP already logged
#     existing_devices = LoginActivity.objects.filter(user=user)
#     is_existing_device = existing_devices.filter(
#         ip_address=ip,
#         browser=browser,
#         os=os
#     ).exists()

#     # Block if it's a new device and user already has 3
#     if not is_existing_device and existing_devices.count() >= 3:
#         request.session['login_block_reason'] = "Login blocked: maximum 3 devices allowed per user."
#         raise PermissionDenied("Too many active devices.")

#     # Save or update login info
#     LoginActivity.objects.update_or_create(
#         user=user,
#         ip_address=ip,
#         browser=browser,
#         os=os,
#         defaults={'last_login': timezone.now()}
#     )

#     # Optionally store latest device info on User model
#     user.browser = browser
#     user.os = os
#     user.ip_address = ip
#     user.save()


# def get_client_ip(request):
#     """Retrieve real IP address even behind proxy/CDN."""
#     x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
#     if x_forwarded:
#         return x_forwarded.split(',')[0].strip()
#     return request.META.get('REMOTE_ADDR')
# @receiver(user_logged_in)
# def save_login_info(sender, request, user, **kwargs):
#     from user_agents import parse
#     user_agent_str = request.META.get('HTTP_USER_AGENT', '')
#     user_agent = parse(user_agent_str)

#     ip = get_client_ip(request)
#     LoginActivity.objects.update_or_create(
#         user=user,
#         ip_address=ip,
#         browser=user_agent.browser.family,
#         os=user_agent.os.family,
#         defaults={'last_login': timezone.now()}
#     )
# logger = logging.getLogger(__name__)
# @receiver(user_logged_in)
# def limit_login_devices(sender, request, user, **kwargs):
#     logger.info(f"[LOGIN ATTEMPT] User: {user}, IP: {request.META.get('REMOTE_ADDR')}")
    


# @receiver(user_logged_in)
# def log_user_login(sender, request, user, **kwargs):
#     x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
#     ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

#     user_agent = request.META.get('HTTP_USER_AGENT', '')
#     ua = user_agents.parse(user_agent)

#     LoginActivity.objects.create(
#         user=user,
#         browser=ua.browser.family,
#         os=ua.os.family,
#         ip=ip
#     )t_client_ip(request):
#     x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
#     if x_forwarded_for:
#         ip = x_forwarded_for.split(',')[0]
#     else:
#         ip = request.META.get('REMOTE_ADDR')
#     return ip