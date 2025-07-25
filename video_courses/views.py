from django.shortcuts import render, get_object_or_404 ,  redirect
from VulnTech_V3.settings import *
from video_courses.models import Courses, course_Lesson, Payment, course_category
from vt_site.models import Terms_pages, site_detail
import razorpay
from django.http import HttpResponse, Http404, JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from time import time
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
import os
import re
from django.core import signing



client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

def get_lessons(request):
    course_id = request.GET.get('course_id')
    lessons = []
    if course_id:
        lessons = course_Lesson.objects.filter(chapter__course_id=course_id).values('id', 'title')
    
    return JsonResponse(list(lessons), safe=False)

# Helper functions for token generation and validation
def generate_video_token(lesson_id, expiry_seconds=60):
    data = {
        'lesson_id': lesson_id,
        'expiry': int(time()) + expiry_seconds,
    }
    return signing.dumps(data)


def validate_video_token(token, lesson_id):
    try:
        data = signing.loads(token, max_age=60)  # token expires in 60 seconds
        if str(data.get('lesson_id')) == str(lesson_id):
            return True
        return False
    except signing.SignatureExpired:
        return False
    except signing.BadSignature:
        return False

def user_has_permission(user, lesson):
    course = lesson.chapter.course
    return Payment.objects.filter(course=course, user=user, status=True).exists()

def courses(request):
    course = Courses.objects.all()
    terms_pages = Terms_pages.objects.all()
    siteDetail = site_detail.objects.all()
    categories = course_category.objects.all()
    context = {
        'course': course,
        'terms_pages': terms_pages,
        'siteDetail': siteDetail,
        'categories': categories,
    }
    return render(request, "courses_pages/all-courses.html", context)


client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

def course_detail(request, slug):
    course = get_object_or_404(Courses, course_slug=slug)
    chapters = course.course_chapter_set.all()
    faqs = course.faqs.all()
    terms_pages = Terms_pages.objects.all()
    siteDetail = site_detail.objects.all()
    # For public access, purchased is always False if user is not authenticated.
    purchased = False
    if request.user.is_authenticated:
        purchased = Payment.objects.filter(course=course, user=request.user, status=True).exists()

    total_duration = chapters.aggregate(total_duration=Sum('course_lesson__duration'))['total_duration']
    if total_duration:
        hours, minutes, *_ = str(total_duration).split(':')
        total_duration = f"{hours}h {minutes}m" if int(hours) > 0 else f"{minutes}m"
    else:
        total_duration = "0m"
    
    total_lessons = chapters.aggregate(total_lessons=Count('course_lesson'))['total_lessons']
    purchase_count = Payment.objects.filter(course=course, status=True).count()
    related_courses = Courses.objects.filter(category=course.category).exclude(id=course.id)[:5]
    order = None
    if request.method == "POST":
        action = request.GET.get("action")
        if action == 'free_enroll' and course.is_free_course:
            Payment.objects.create(course=course, user=request.user, status=True)
        elif action == 'payment' and request.user.is_authenticated:
            user_name = request.user.username
            email = request.user.email
            mobile = str(request.user.mobile)
            amount = int(course.price * 100)
            currency = "INR"
            notes = {
                "name": user_name,
                "phone": mobile,
                "email": email,
            }
            receipt = f"Vulntech-{int(time())}"
            try:
                order = client.order.create({
                    'receipt': receipt,
                    'notes': notes,
                    'amount': amount,
                    'currency': 'INR',
                })
                payment = Payment(
                    course=course,
                    user=request.user,
                    order_id=order.get('id')
                )
                payment.save()
            except Exception as e:
                print(f"Error creating payment: {e}")

    context = {
        'course': course,
        'order': order,
        'chapters': chapters,
        'faqs': faqs,
        'terms_pages': terms_pages,
        'siteDetail': siteDetail,
        'purchased': purchased,
        'total_duration': total_duration,
        'total_lessons': total_lessons,
        'purchase_count': purchase_count,
        'related_courses': related_courses,
        'intro_video': course.intro_video,
    }
    return render(request, "courses_pages/course_desc.html", context)


@csrf_exempt
def verify_payment(request):
    if request.method == "POST":
        data = request.POST
        try:
            siteDetail = site_detail.objects.all()
            terms_pages = Terms_pages.objects.all()
            client.utility.verify_payment_signature(data)
            razorpay_order_id = data['razorpay_order_id']
            razorpay_payment_id = data['razorpay_order_id']
            payment = Payment.objects.get(order_id=razorpay_order_id)
            payment.payment_id = razorpay_payment_id
            payment.status = True
            payment.save()
            context = {
                'data': data,
                'payment': payment,
                'terms_pages': terms_pages,
                'siteDetail': siteDetail,
            }
            return render(request, "courses_pages/verify_payments/success.html", context)
        except:
            return render(request, "courses_pages/verify_payments/failure.html")

@login_required(login_url="login")
def course_content(request, slug, lesson_slug):
    course = get_object_or_404(Courses, course_slug=slug)
    chapters = course.course_chapter_set.all()
    if lesson_slug == 'None':
        first_lesson = chapters[0].course_lesson_set.first() if chapters else None
        if first_lesson:
            lesson_slug = first_lesson.slug
    lesson = get_object_or_404(course_Lesson, slug=lesson_slug)
    previous_lesson = course_Lesson.objects.filter(chapter=lesson.chapter, id__lt=lesson.id).last()
    next_lesson = course_Lesson.objects.filter(chapter=lesson.chapter, id__gt=lesson.id).first()
    terms_pages = Terms_pages.objects.all()
    siteDetail = site_detail.objects.all()
    # Generate a token for secure streaming for this lesson
    token = generate_video_token(lesson.id, expiry_seconds=60)
    context = {
        'course': course,
        'chapters': chapters,
        'lesson': lesson,
        'slug': slug,
        'previous_lesson': previous_lesson,
        'next_lesson': next_lesson,
        'terms_pages': terms_pages,
        'siteDetail': siteDetail,
        'video_token': token,  # Pass the token to the template
    }
    return render(request, "courses_pages/video_page.html", context)

@login_required(login_url="login")
def my_courses(request):
    terms_pages = Terms_pages.objects.all()
    siteDetail = site_detail.objects.all()
    cache_key = f"my_courses_{request.user.id}"
    purchased_courses = cache.get(cache_key)
    if not purchased_courses:
        purchased_courses = Courses.objects.filter(
            payment__user=request.user, payment__status=True
        ).distinct().prefetch_related('payment_set')
        cache.set(cache_key, purchased_courses, 300)
    context = {
        'purchased_courses': purchased_courses,
        'terms_pages': terms_pages,
        'siteDetail': siteDetail,
    }
    return render(request, "courses_pages/my_courses.html", context)

# ------------------------------
# Secure video streaming view with chunk support and download limitation
# ------------------------------
@login_required(login_url="login")
def stream_video(request, lesson_slug):
    lesson = get_object_or_404(course_Lesson, slug=lesson_slug)
    
    # Ensure a video file is associated
    if not lesson.video_upload:
        raise Http404("Video not available.")
    
    # Check user permission
    if not user_has_permission(request.user, lesson):
        raise PermissionDenied("You do not have permission to view this video.")
    
    video_path = lesson.video_upload.path
    if not os.path.exists(video_path):
        raise Http404("Video file not found.")
    
    file_size = os.path.getsize(video_path)
    
    # Determine if the request is from a legitimate viewer.
    # First, check for a short-lived token; fallback to cookie.
    token = request.GET.get("token")
    if token and validate_video_token(token, lesson.id):
        full_stream = True
    else:
        full_stream = (request.COOKIES.get('full_stream') == 'true')
    
    # If neither method indicates full access, limit to 10% of the file.
    allowed_bytes = file_size if full_stream else int(file_size * 0.1)
    
    range_header = request.META.get('HTTP_RANGE', '').strip()
    
    if range_header:
        range_match = re.match(r'bytes=(\d+)-(\d*)', range_header)
        if range_match:
            start_str, end_str = range_match.groups()
            try:
                start = int(start_str)
            except ValueError:
                start = 0
            requested_end = int(end_str) if end_str else file_size - 1
            # Do not allow serving beyond our allowed_bytes limit.
            end = requested_end if requested_end < allowed_bytes else allowed_bytes - 1
        else:
            start = 0
            end = allowed_bytes - 1
        
        length = end - start + 1
        with open(video_path, 'rb') as f:
            f.seek(start)
            data = f.read(length)
        
        response = HttpResponse(data, status=206, content_type='video/mp4')
        response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
        response['Content-Length'] = str(length)
    else:
        # If no Range header, read up to allowed_bytes bytes.
        with open(video_path, 'rb') as f:
            data = f.read(allowed_bytes)
        response = HttpResponse(data, content_type='video/mp4')
    
    # Security headers
    response['Cache-Control'] = 'private, no-store, max-age=0, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    response['X-Content-Type-Options'] = 'nosniff'
    
    return response
