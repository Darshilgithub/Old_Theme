from django.core.exceptions import PermissionDenied
from account.models import LoginActivity

class DeviceLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            ip = get_client_ip(request)
            device_count = LoginActivity.objects.filter(user=request.user).count()
            if device_count > 3 and not LoginActivity.objects.filter(user=request.user, ip_address=ip).exists():
                raise PermissionDenied("Device limit exceeded.")
        return self.get_response(request)

def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
