# from django.contrib.auth.backends import ModelBackend
# from django.core.exceptions import PermissionDenied
# from .models import LoginActivity
# from user_agents import parse


# class DeviceLimitBackend(ModelBackend):
#     def authenticate(self, request, username=None, password=None, **kwargs):
#         user = super().authenticate(request, username=username, password=password, **kwargs)
#         if user and request:
#             ip = self.get_client_ip(request)
#             user_agent_str = request.META.get('HTTP_USER_AGENT', '')
#             user_agent = parse(user_agent_str)

#             browser = user_agent.browser.family
#             os = user_agent.os.family

#             existing_devices = LoginActivity.objects.filter(user=user)
#             device_exists = existing_devices.filter(
#                 ip_address=ip,
#                 browser=browser,
#                 os=os
#             ).exists()

#             if not device_exists and existing_devices.count() >= 3:
#                 raise PermissionDenied("Login blocked: more than 3 devices used")

#         return user

#     def get_client_ip(self, request):
#         x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
#         if x_forwarded_for:
#             return x_forwarded_for.split(',')[0]
#         return request.META.get('REMOTE_ADDR')

from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import PermissionDenied
from .models import LoginActivity
from user_agents import parse


class DeviceLimitBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = super().authenticate(request, username=username, password=password, **kwargs)
        if user and request:
            ip = self.get_client_ip(request)
            user_agent_str = request.META.get('HTTP_USER_AGENT', '')
            user_agent = parse(user_agent_str)

            browser = user_agent.browser.family
            os = user_agent.os.family

            existing_devices = LoginActivity.objects.filter(user=user)
            device_exists = existing_devices.filter(
                ip_address=ip,
                browser=browser,
                os=os
            ).exists()

            if not device_exists and existing_devices.count() >= 3:
                raise PermissionDenied("Login blocked: more than 3 devices used")

        return user

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
