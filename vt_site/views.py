from django.shortcuts import get_object_or_404, redirect, render
from django.templatetags.static import static
from django.conf import settings as conf_settings
from django.contrib import messages
from tutorial.models import *
from video_courses.models import * 
from video_courses.models import Courses, course_category
from vt_site.models import *
from django.core.mail import send_mail
from django.utils import timezone
from django.http import JsonResponse
from datetime import date, timedelta


def index(request):
    terms_pages = Terms_pages.objects.all()
    tutorialsCategory = tutorial_category.objects.all().order_by('id')[:6]
    coursesCategory = course_category.objects.all().order_by('id')[:6]
    featured_courses = Courses.objects.filter(is_free_course=True).order_by('-id')[:6]
    plans = Plan.objects.all()
    siteDetail = site_detail.objects.all()
    
    context = {
        'tutorialsCategory': tutorialsCategory,
        'coursesCategory': coursesCategory,
        'featured_courses': featured_courses,
        'terms_pages': terms_pages,
        'plans': plans,
        'siteDetail': siteDetail,
    }
    return render(request, "main_elements/index.html", context)

def about(request):
    terms_pages = Terms_pages.objects.all()
    team = Teammate.objects.all()
    siteDetail = site_detail.objects.all()
    context = {
        'terms_pages': terms_pages,
        'team': team,
        'siteDetail': siteDetail,
    }
    return render(request, "main_elements/aboutus.html", context)

def contact(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            name = request.POST['name']
            subject = request.POST['subject']
            content = request.POST['content']

            sub = subject
            msg = f'''Dear VulnTech Team,

{request.user.email} user sent this mail. The message from {name} is below.

{content} 

With regards,
{name}'''
        
            from_email = conf_settings.EMAIL_HOST_USER
            to = conf_settings.DEFAULT_FROM_EMAIL
            try:
                user_feedback_time = request.user.feedback_last_sent_at
                if user_feedback_time is None or user_feedback_time + timezone.timedelta(minutes=15) < timezone.now():
                    send_mail(sub, msg, from_email, [to])
                    messages.success(request, "Form Submitted Successfully")
                    request.user.feedback_last_sent_at = timezone.now()
                    request.user.save()
                else:
                    messages.error(request, "Please wait for 15 minutes between feedback submissions.")
                return redirect('contact')
            except Exception:   
                messages.error(request, "Something went wrong, try again later.")
                return redirect('contact')
        else:
            messages.error(request, "Please log in to submit the form.")
            return redirect('contact')
    else:
        terms_pages = Terms_pages.objects.all()
        siteDetail = site_detail.objects.all()
        context = {
            'terms_pages': terms_pages,
            'siteDetail': siteDetail,
        }
        return render(request, "main_elements/contactus.html", context)

def plans(request):
    terms_pages = Terms_pages.objects.all()
    siteDetail = site_detail.objects.all()
    context = {
        'terms_pages': terms_pages,
        'siteDetail': siteDetail,
    }
    return render(request, "main_elements/plans.html", context)

def maintenance(request):
    return render(request, "maintenance_pages/maintenance.html")

def privacy(request, slug):
    terms_pages = Terms_pages.objects.all()
    terms = get_object_or_404(Terms_pages, slug=slug)
    siteDetail = site_detail.objects.all()
    context = {
        'terms': terms,
        'terms_pages': terms_pages,
        'siteDetail': siteDetail,
    }
    return render(request, "main_elements/terms_pages.html", context)

def handel404(request, exception):
    return render(request, "maintenance/404.html")

def faq(request):
    faq_category = FAQ_cate.objects.all().order_by('id')
    siteDetail = site_detail.objects.all()
    faq = FAQ.objects.all()
    terms_pages = Terms_pages.objects.all()
    context = {
        'faq': faq,
        'faq_category': faq_category,
        'terms_pages': terms_pages,
        'siteDetail': siteDetail,
    }
    return render(request, "main_elements/faq.html", context)

def my_dashboard(request):
    return render(request, 'main_elements/my_dashboard.html')
