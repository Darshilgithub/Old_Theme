from datetime import date
from .models import UserActivity
def get_client_info(request):
    """Returns IP address, browser, and OS from request."""
    from user_agents import parse

    user_agent_str = request.META.get('HTTP_USER_AGENT', '')
    user_agent = parse(user_agent_str)

    ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if ip:
        ip = ip.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')

    browser = f"{user_agent.browser.family} {user_agent.browser.version_string}"
    os = f"{user_agent.os.family} {user_agent.os.version_string}"

    return ip, browser, os

def log_user_activity(user):
    today = date.today()
    obj, created = UserActivity.objects.get_or_create(user=user, date=today)
    obj.count += 1 if not created else 0
    obj.save()