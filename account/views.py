from datetime import datetime
import random
from .models import UserActivity
from urllib import request
from datetime import date

from django.conf import settings as conf_settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login as user_login, logout as user_logout
from django.contrib import messages
from django.urls import reverse_lazy
from phonenumber_field.phonenumber import to_python
from phonenumbers import region_code_for_country_code
from django.core.mail import send_mail
from account.forms import *
from account.utils import log_user_activity
from vt_site.models import Terms_pages, site_detail
from .models import *
from django.utils import timezone
from django.contrib.auth.views import *
from django.contrib.auth.decorators import login_required
from user_agents import parse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from phonenumber_field.phonenumber import to_python
from user_agents import parse
import random
from account.models import User
from vt_site.models import Terms_pages, site_detail
from django.conf import settings as conf_settings
from django.core.exceptions import PermissionDenied
import user_agents
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import UserActivity
from datetime import timedelta


def login(request):
    if request.user.is_authenticated:
        return redirect("index")
    if request.method == 'POST':
        password = request.POST['password']
        mobile = request.POST['mobile']
        
        mobile = to_python(mobile)
        
        user = authenticate(request, mobile = mobile, password = password)

        if user is not None:
            user_login(request, user)
            return redirect('/')
        else:
            messages.info(request,'Invalid Mobile Number/password')
            return redirect('login') 
    else:
        terms_pages = Terms_pages.objects.all()
        siteDetail = site_detail.objects.all()
        context = {
            'terms_pages' : terms_pages,
            'siteDetail' : siteDetail,
        }
        return render(request, 'registration/login.html', context)


def register(request):
    if request.user.is_authenticated:
        return redirect("index")
    
    if request.method == 'POST':
        f_name = request.POST['f_name']
        l_name = request.POST['l_name']
        email = request.POST['email']
        mobile = request.POST['register_mobile']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        mobile = to_python(mobile)

        existing_mobile_user = User.objects.filter(mobile=mobile).first()
        existing_email_user = User.objects.filter(email=email).first()

        if not mobile.is_valid():
            messages.info(request, "Invalid Mobile Number")
            return redirect('register')
        elif existing_mobile_user:
            masked_email = f"{existing_mobile_user.email[:2]}{'X'*5}{existing_mobile_user.email[-13:]}"
            messages.info(request, f"Hold on! Mobile Number is already linked to a ({masked_email}).")
            return redirect('register')
        elif existing_email_user:
            masked_mobile = f"{str(existing_email_user.mobile)[:3]}{'X'*5}{str(existing_email_user.mobile)[-4:]}"
            messages.info(request, f"Watch out! Email Address is connected to a ({masked_mobile}).")
            return redirect('register')
        elif password != confirm_password:
            messages.info(request, "Confirm Password not match with the Password")
            return redirect('register')
        else:
            otp = str(random.randint(10000, 99999))
            masked_email = f"{email[:2]}{'X'*5}{email[-13:]}"
            verify_otp_data = {
                'first_name': f_name,
                'last_name': l_name,
                'username': f_name,
                'email': email,
                'mobile': str(mobile),
                'password': password,
                'otp': otp,
                'masked_email': masked_email,
                'action': "register",
                'time': str(timezone.now())
            }

            request.session['verify_otp_data'] = verify_otp_data

            # ✅ Detect user device info
            user_agent_str = request.META.get('HTTP_USER_AGENT', '')
            print("REGISTER USER-AGENT:", user_agent_str)

            user_agent = parse(user_agent_str)
            request.session['user_device_info'] = {
                'browser': user_agent.browser.family,
                'os': user_agent.os.family,
                'device': user_agent.device.family
            }

            # Send OTP email
            sub = "Your VulnTech Account - One-Time Password (OTP)"
            msg = f'''Dear {f_name},

Greetings from VulnTech!

    To ensure the security of your account, we are providing you with a one-time password (OTP) for authentication. Please use the following OTP to complete your login:

OTP: {otp}

    If you did not attempt to log in or requested this OTP, please contact our support team immediately.

    Thank you for choosing VulnTech. We prioritize the safety and privacy of your account.

Best Regards,
VulnTech Support Team

---

*Note: This is an automated message. Please refrain from replying directly. For assistance or inquiries, kindly connect with our dedicated support team at support@vulntech.com. Thank you.*
'''

            from_email = conf_settings.EMAIL_HOST_USER
            to = [email]
            try:
                send_mail(sub, msg, from_email, to)
            except Exception as e:
                print(e)
                messages.error(request, "Something went wrong! please try again later")

            return redirect('verify_otp')

    else:
        terms_pages = Terms_pages.objects.all()
        siteDetail = site_detail.objects.all()
        context = {
            'terms_pages': terms_pages,
            'siteDetail': siteDetail,
        }
        return render(request, 'registration/signup.html', context)


def otpVerify(request): 
    user_data = request.session.get('verify_otp_data')
    user_agent_str = request.META.get('HTTP_USER_AGENT', '')
    user_agent = parse(user_agent_str)

    if not user_data:
        messages.error(request, "Something went wrong! please try again")
        return redirect('index')
    if datetime.strptime(user_data['time'],"%Y-%m-%d %H:%M:%S.%f%z") + timezone.timedelta(minutes=10) < timezone.now():
        request.session.pop('verify_otp_data', None)

    if request.method == 'POST':
        otp_1 = request.POST.get('otp_1')
        otp_2 = request.POST.get('otp_2')
        otp_3 = request.POST.get('otp_3')
        otp_4 = request.POST.get('otp_4')
        otp_5 = request.POST.get('otp_5')  

        combined_otp = f"{otp_1}{otp_2}{otp_3}{otp_4}{otp_5}"

        
        if combined_otp == user_data['otp']:
            if user_data['action'] == 'register':
                user = User.objects.create_user(
                        

                        first_name=user_data['first_name'],
                        last_name=user_data['last_name'],
                        username=user_data['username'],
                        email=user_data['email'],
                        mobile = to_python(user_data['mobile']),
                        password=user_data['password']
                        
                )
                device_info = request.session.get('user_device_info')
                print("DEVICE INFO IN SESSION:", request.session.get('user_device_info'))

                if not device_info:
    # fallback: parse again from this request
                    user_agent_str = request.META.get('HTTP_USER_AGENT', '')
                    print("Fallback user-agent string:", user_agent_str)
                    user_agent = parse(user_agent_str)
                    user.browser = user_agent.browser.family
                    user.os = user_agent.os.family
                    user.device = user_agent.device.family
                else:
                    user.browser = device_info.get('browser', '')
                    user.os = device_info.get('os', '')
                    user.device = device_info.get('device', '')

                user.save()
                
                user_login(request, user)            
                masked_mobile = f"{user_data['mobile'][:3]}{'X'*5}{user_data['mobile'][-4:]}"

                sub = "Welcome to VulnTech - Your Account is Ready!"            
                msg = f"""Dear {user_data['first_name']},

We are delighted to welcome you to VulnTech!

Your account has been successfully created, and you are now part of a our learning community. VulnTech offers a diverse range of tutorials and video courses to help you expand your knowledge and skills.

Key Features:
- In-depth Tutorials
- Expert-led Video Courses
- Interactive Learning Resources

To get started, simply log in with your registered mobile and password. 
Mobile Number : {masked_mobile}
Login Link  :  https://www.vulntech.com/accounts/login

Thank you for choosing VulnTech. We are committed to providing you with valuable resources to support your learning journey.


Best Regards,
The VulnTech Team

---

*Note: This is an automated message. Please refrain from replying directly. For assistance or inquiries, kindly connect with our dedicated support team at support@vulntech.com. Thank you.*

"""

                from_email = conf_settings.EMAIL_HOST_USER
                to = [user_data['email']]
                try:
                    send_mail(sub, msg, from_email, to)
                    request.session.pop('verify_otp_data', None)
                except Exception:
                    messages.error(request,"Something went wrong! please try again later")
                return redirect('index')
            
            elif user_data['action'] == 'ChangeMobile':
                try:
                    request.user.mobile = to_python(user_data['mobile'])
                    request.user.save()
                    messages.success(request, "Mobile Changed Successfully")
                    request.session.pop('verify_otp_data', None)
                    user_logout(request,request.user)
                    return redirect('login')
                except Exception:
                    messages.error(request, "Error in Changing Mobile. Try again later")
                    request.session.pop('verify_otp_data', None)
                    return redirect("mobileChange")
                
            elif user_data['action'] == 'ChangeEmail':
                try:
                    request.user.email = user_data['email']
                    request.user.save()
                    messages.success(request, "Email Changed Successfully")
                    request.session.pop('verify_otp_data', None)
                    user_logout(request)
                    return redirect('login')
                except Exception:
                    messages.error(request, "Error in Changing Email. Try again later")
                    request.session.pop('verify_otp_data', None)
                    return redirect("emailChange")
            elif user_data['action'] == 'ChangePass':
                try:
                    request.user.set_password(user_data['password'])
                    request.user.save()
                    messages.success(request, "Password Changed Successfully")
                    request.session.pop('verify_otp_data', None)
                    user_logout(request)
                    return redirect('login')
                except Exception as e:
                    messages.error(request, "Error in Changing Password. Try again later")
                    request.session.pop('verify_otp_data', None)
                    return redirect("emailChange")
        else:
            messages.error(request, "Wrong otp entered.")
            return redirect('verify_otp')
            user_agent_str = request.META.get('HTTP_USER_AGENT', '')
            user_agent = parse(user_agent_str)
            request.session['user_device_info'] = {
                'browser': user_agent.browser.family,
                'os': user_agent.os.family,
                'device': user_agent.device.family
            }
    
    else:
        terms_pages = Terms_pages.objects.all()
        siteDetail = site_detail.objects.all()
        context = {
            'masked_email' : user_data['masked_email'],
            'terms_pages' : terms_pages,
            'siteDetail' : siteDetail,
        }
        return render(request, 'registration/verifyotp.html', context)
    

def resend_otp(request):
    user_data = request.session.get('verify_otp_data')

    if not user_data:
        messages.error(request, "User registration details not found.")
        return redirect('register')

    new_otp = str(random.randint(10000, 99999)) 
    user_data['otp'] = new_otp
    request.session['verify_otp_data'] = user_data

    sub = "Your VulnTech Account - One-Time Password (OTP)"
            
    msg = f"""Dear {user_data['username']},

Greetings from VulnTech!

    To ensure the security of your account, we are providing you with a one-time password (OTP) for authentication. Please use the following OTP to complete your login:

OTP: {new_otp}

    If you did not attempt to log in or requested this OTP, please contact our support team immediately.

    Thank you for choosing VulnTech. We prioritize the safety and privacy of your account.

Best Regards,
VulnTech Support Team

---

*Note: This is an automated message. Please refrain from replying directly. For assistance or inquiries, kindly connect with our dedicated support team at support@vulntech.com. Thank you.*

"""

    from_email = conf_settings.EMAIL_HOST_USER
    to = [user_data['email']]
    try:
        send_mail(sub, msg, from_email, to)
    except Exception:
        messages.error(request,"Something went wrong! please try again later")
  # Implement this function to send the email

    return JsonResponse({'success': True})

@login_required(login_url="login")
def profile(request):
    terms_pages = Terms_pages.objects.all()
    siteDetail = site_detail.objects.all()
    context = {    
        'siteDetail' : siteDetail,
        'terms_pages' : terms_pages,
    }
    return render(request, 'registration/profile.html', context)


class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/forgot_pass.html'
    
    def form_valid(self, form):
        email = form.cleaned_data['email']
        try:
            user = User.objects.get(email=email)
            user.password_reset_sent_at = timezone.now()
            user.reset_link_valid = True
            user.save()
            return super().form_valid(form)
        except User.DoesNotExist:
            return super().form_valid(form)
        

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/Passreset_s.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        if hasattr(self, 'user') and self.user is not None:
            self.user.reset_link_valid = False
            self.user.save()
        else:
            print("Not valid link set as false")
        
        return response
    
    def form_invalid(self, form):
        combined_errors = list(form.non_field_errors()) + list(form['new_password1'].errors) + list(form['new_password2'].errors)
        context = self.get_context_data(form=form, combined_errors=combined_errors)
        return self.render_to_response(context)
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        terms_pages = Terms_pages.objects.all()
        siteDetail = site_detail.objects.all()
        if self.user.reset_link_valid:
            now = timezone.now()
            t = self.user.password_reset_sent_at + timezone.timedelta(minutes=30) > now
            self.user.reset_link_valid = t
            context['valid_link'] = t
            context['terms_pages'] = terms_pages
            context['siteDetail'] = siteDetail
            self.user.save()
        else:
            context['valid_link'] = False
            context['terms_pages'] = terms_pages
            context['siteDetail'] = siteDetail
        return context


@login_required(login_url="login")
def profile_view(request):
    terms_pages = Terms_pages.objects.all()
    siteDetail = site_detail.objects.all()
    context = {
        'terms_pages' : terms_pages,
        'siteDetail' : siteDetail,
    }
    return render(request, 'registration/view_profile.html', context)

@login_required(login_url="login")
def profile_edit(request):
    user = request.user

    if request.method == 'POST':
        try:
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.username = request.POST.get('username')
            if 'pic' in request.FILES:
                user.pic = request.FILES['pic']

            user.save()
            messages.success(request, "Profile Updated Successfully")
            return redirect('edit_profile')
        except Exception:
            messages.error(request, "Error in updating profile. Try again")
            return redirect("edit_profile")
    else: 
        form = UserForm(instance=user)
        countryCode = region_code_for_country_code(user.mobile.country_code)
        terms_pages = Terms_pages.objects.all()
        siteDetail = site_detail.objects.all()
        context = {
            'form': form,
            'countryCode' : countryCode,
            'terms_pages' : terms_pages,
            'siteDetail' : siteDetail,
        }
        return render(request, 'registration/edit_profile.html', context)


@login_required(login_url="login")
def settings(request):
    terms_pages = Terms_pages.objects.all()
    siteDetail = site_detail.objects.all()
    context = {
        'terms_pages' : terms_pages,
        'siteDetail' : siteDetail,
    }
    return render(request, 'registration/settings.html', context)

@login_required(login_url="login")
def account_info(request):
    terms_pages = Terms_pages.objects.all()
    siteDetail = site_detail.objects.all()
    context = {
        'terms_pages' : terms_pages,
        'siteDetail' : siteDetail,
    }
    return render(request, 'registration/account_info.html', context)

@login_required(login_url="login")
def delete_account(request):
    request.user.delete()
    user_logout(request) 
    return redirect('index')

@login_required(login_url="login")
def mobileChange(request):
    user = request.user

    if request.method == 'POST':
        mobile = request.POST.get('mobile')
        mobile = to_python(mobile)

        existing_mobile_user = User.objects.filter(mobile=mobile).first()
        
        if not mobile.is_valid():
            messages.error(request, "Invalid Mobile Number")
            return redirect('mobileChange')
        elif to_python(user.mobile) == mobile:
            messages.info(request, "Retained the prior mobile number, no changes made.")
            return redirect('mobileChange')
        elif existing_mobile_user:
            masked_email = f"{existing_mobile_user.email[:2]}{'X'*5}{existing_mobile_user.email[-13:]}"
            messages.error(request, f"Hold on! Mobile Number is already linked to a ({masked_email}).")
            return redirect('mobileChange')
        else:
            otp = str(random.randint(10000, 99999))
            masked_email = f"{user.email[:2]}{'X'*5}{user.email[-13:]}"
            verify_otp_data = {
                'mobile': str(mobile),
                'otp': otp,
                'masked_email': masked_email,
                'username': user.username,
                'action': "ChangeMobile",
                'time' : str(timezone.now())
            }

            request.session['verify_otp_data'] = verify_otp_data
            
                
            sub = "Your VulnTech Account - One-Time Password (OTP)"
                
            msg = f'''Dear {user.username},

Greetings from VulnTech!

You have initiated a mobile number change for your account. Please find your One-Time Password (OTP) below:

OTP: {otp}

If you did not request this change or are unsure about this activity, please contact our support team immediately.

Thank you for choosing VulnTech. We prioritize the safety and privacy of your account.

Best Regards,
VulnTech Support Team

---

*Note: This is an automated message. Please refrain from replying directly. For assistance or inquiries, kindly connect with our dedicated support team at support@vulntech.com. Thank you.*
'''

            from_email = conf_settings.EMAIL_HOST_USER
            to = [user.email]
            try:
                send_mail(sub, msg, from_email, to)
            except Exception:
                messages.error(request,"Something went wrong! please try again later")
            return redirect('verify_otp')
            user_agent = parse(user_agent_str)
            request.session['user_device_info'] = {
                'browser': user_agent.browser.family,
                'os': user_agent.os.family,
                'device': user_agent.device.family
            }
    else: 
        form = UserForm1(instance=user)
        countryCode = region_code_for_country_code(user.mobile.country_code)
        terms_pages = Terms_pages.objects.all()
        siteDetail = site_detail.objects.all()
        context = {
            'form': form,
            'countryCode' : countryCode,
            'terms_pages' :terms_pages,
            'siteDetail' : siteDetail,
        }
        return render(request, 'registration/mobileChange.html', context)

@login_required(login_url="login")
def emailChange(request):
    user = request.user

    if request.method == 'POST':
        email = request.POST.get('email')
        existing_email_user = User.objects.filter(email=email).first()
        
        if existing_email_user:
            masked_mobile = f"{str(existing_email_user.mobile)[:3]}{'X'*5}{str(existing_email_user.mobile)[-4:]}"
            messages.info(request, f"Watch out! Email Address is connected to a ({masked_mobile}).")
            return redirect('emailChange')
        elif to_python(user.email) == email:
            messages.info(request, "Retained the prior email, no changes made.")
            return redirect('emailChange')
        else:
            otp = str(random.randint(10000, 99999))
            masked_email = f"{email[:2]}{'X'*5}{email[-13:]}"
            verify_otp_data = {
                'email': email,
                'otp': otp,
                'masked_email': masked_email,
                'username': user.username,
                'action': "ChangeEmail",
                'time' : str(timezone.now())
            }

            request.session['verify_otp_data'] = verify_otp_data
            
                
            sub = "Your VulnTech Account - One-Time Password (OTP)"
                
            msg = f'''Dear {user.username},

Greetings from VulnTech!

You have initiated a email id change for your account. Please find your One-Time Password (OTP) below:

OTP: {otp}

If you did not request this change or are unsure about this activity, please contact our support team immediately.

Thank you for choosing VulnTech. We prioritize the safety and privacy of your account.

Best Regards,
VulnTech Support Team

---

*Note: This is an automated message. Please refrain from replying directly. For assistance or inquiries, kindly connect with our dedicated support team at support@vulntech.com. Thank you.*
'''

            from_email = conf_settings.EMAIL_HOST_USER
            to = [email]
            try:
                send_mail(sub, msg, from_email, to)
            except Exception:
                messages.error(request,"Something went wrong! please try again later")
            return redirect('verify_otp')
        
    else: 
        form = UserForm1(instance=user)
        terms_pages = Terms_pages.objects.all()
        siteDetail = site_detail.objects.all()
        context = {
            'form': form,
            'terms_pages' : terms_pages,
            'siteDetail' : siteDetail
        }
        return render(request, 'registration/emailChange.html', context)



class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'registration/PassChange.html'
    success_url = reverse_lazy("verify_otp")

    def form_valid(self, form):
        user = self.request.user
        otp = str(random.randint(10000, 99999))
        masked_email = f"{user.email[:2]}{'X'*5}{user.email[-13:]}"
        verify_otp_data = {
            'password': form.cleaned_data['new_password1'],
            'otp': otp,
            'masked_email': masked_email,
            'username': user.username,
            'action': "ChangePass",
            'time' : str(timezone.now())
        }
        self.request.session['verify_otp_data'] = verify_otp_data
        
        # Compose and send OTP email
        sub = "Your VulnTech Account - One-Time Password (OTP)"
        msg = f'''Dear {user.username},

Greetings from VulnTech!

You have initiated a Password change for your account. Please find your One-Time Password (OTP) below:

OTP: {otp}

If you did not request this change or are unsure about this activity, please contact our support team immediately.

Thank you for choosing VulnTech. We prioritize the safety and privacy of your account.

Best Regards,
VulnTech Support Team

---

*Note: This is an automated message. Please refrain from replying directly. For assistance or inquiries, kindly connect with our dedicated support team at support@vulntech.com. Thank you.*
'''
        from_email = conf_settings.EMAIL_HOST_USER
        to = [user.email]
        try:
            send_mail(sub, msg, from_email, to)
        except Exception:
            messages.error(self.request,"Something went wrong! please try again later")
            
        # Continue with the default behavior
        return super().form_valid(form)

    def form_invalid(self, form):
        combined_errors = list(form.non_field_errors()) + list(form['old_password'].errors) + list(form['new_password1'].errors) + list(form['new_password2'].errors)
        terms_pages = Terms_pages.objects.all()
        siteDetail = site_detail.objects.all()
        context = self.get_context_data(form=form, combined_errors=combined_errors,terms_pages=terms_pages,siteDetail=siteDetail)
        return self.render_to_response(context)
    
@login_required(login_url="login")
def support(request):
    account_faq_category = account_FAQ_cate.objects.all().order_by('id')
    account_faq = account_FAQ.objects.all()
    terms_pages = Terms_pages.objects.all()
    siteDetail = site_detail.objects.all()
    context = {
        'account_faq': account_faq,
        'account_faq_category' : account_faq_category,
        'terms_pages' : terms_pages,
        'siteDetail' : siteDetail,
    }
    return render(request, 'registration/help&support.html', context)


def custom_permission_denied_view(request, reason=""):
    return render(request, '403_device_limit.html', {
        "reason": reason
    }, status=403)
    
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

def log_login_activity(request, user):
    user_agent_string = request.META.get('HTTP_USER_AGENT', '')
    user_agent = parse(user_agent_string)

    LoginActivity.objects.create(
        user=user,
        ip_address=get_client_ip(request),
        browser=user_agent.browser.family,
        os=user_agent.os.family
    )
    
def custom_permission_denied_view(request, reason):
    return render(request, '403_csrf.html', {
        'title': 'Forbidden',
        'message': 'CSRF verification failed. Please reload and try again.',
        'reason': reason
    }, status=403)

def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')

def logout_view(request):
    if request.user.is_authenticated:
        user = request.user
        ip = get_client_ip(request)
        user_agent = parse(request.META.get('HTTP_USER_AGENT', ''))
        browser = user_agent.browser.family
        os = user_agent.os.family

        # Remove this device from LoginActivity
        LoginActivity.objects.filter(
            user=user,
            ip_address=ip,
            browser=browser,
            os=os
        ).delete()

    logout(request)
    return redirect('login')


# from datetime import datetime
# import random
# import bleach
# from urllib import request
# from django.conf import settings as conf_settings
# from django.http import JsonResponse
# from django.shortcuts import get_object_or_404, redirect, render
# from django.contrib.auth import authenticate, login as user_login, logout as user_logout
# from django.contrib import messages
# from django.urls import reverse_lazy
# from phonenumber_field.phonenumber import to_python
# from phonenumbers import region_code_for_country_code
# from django.core.mail import send_mail
# from account.forms import *
# from vt_site.models import Terms_pages, site_detail
# from .models import *
# from django.utils import timezone
# from django.contrib.auth.views import *
# from django.contrib.auth.decorators import login_required
# from PIL import Image
# from io import BytesIO
# from django.core.files.uploadedfile import InMemoryUploadedFile

# def login(request):
#     if request.user.is_authenticated:
#         return redirect("index")
#     if request.method == 'POST':
#         # Sanitize inputs with bleach
#         password = bleach.clean(request.POST.get('password', ''))
#         mobile_input = bleach.clean(request.POST.get('mobile', ''))
        
#         mobile = to_python(mobile_input)
#         user = authenticate(request, mobile=mobile, password=password)

#         if user is not None:
#             user_login(request, user)
#             return redirect('/')
#         else:
#             messages.info(request, 'Invalid Mobile Number/password')
#             return redirect('login')
#     else:
#         terms_pages = Terms_pages.objects.all()
#         siteDetail = site_detail.objects.all()
#         context = {
#             'terms_pages': terms_pages,
#             'siteDetail': siteDetail,
#         }
#         return render(request, 'registration/login.html', context)


# def register(request):
#     if request.user.is_authenticated:
#         return redirect("index")

#     if request.method == 'POST':
#         # Clean user input with bleach
#         f_name = bleach.clean(request.POST.get('f_name', '')).strip()
#         l_name = bleach.clean(request.POST.get('l_name', '')).strip()
#         email = bleach.clean(request.POST.get('email', '')).strip()
#         mobile_input = bleach.clean(request.POST.get('register_mobile', '')).strip()
#         password = request.POST.get('register_password', '').strip()
#         confirm_password = request.POST.get('confirm_password', '').strip()


#         mobile = to_python(mobile_input)
#         if not mobile or not mobile.is_valid():
#             messages.info(request, "Invalid Mobile Number")
#             return redirect('register')

#         existing_mobile_user = User.objects.filter(mobile=mobile).first()
#         existing_email_user = User.objects.filter(email=email).first()

#         if existing_mobile_user:
#             masked_email = f"{existing_mobile_user.email[:2]}{'X'*5}{existing_mobile_user.email[-13:]}"
#             messages.info(request, f"Hold on! Mobile Number is already linked to a ({masked_email}).")
#             return redirect('register')
#         if existing_email_user:
#             masked_mobile = f"{str(existing_email_user.mobile)[:3]}{'X'*5}{str(existing_email_user.mobile)[-4:]}"
#             messages.info(request, f"Watch out! Email Address is connected to a ({masked_mobile}).")
#             return redirect('register')

#         if not password or not confirm_password:
#             messages.info(request, "Password fields cannot be empty")
#             return redirect('register')
#         if password != confirm_password:
#             messages.info(request, "Confirm Password does not match the Password")
#             return redirect('register')
#         else:
#             otp = str(random.randint(10000, 99999))
#             masked_email = f"{email[:2]}{'X'*5}{email[-13:]}"
#             verify_otp_data = {
#                 'first_name': f_name,
#                 'last_name': l_name,
#                 'username': f_name,
#                 'email': email,
#                 'mobile': str(mobile),
#                 'password': password,
#                 'otp': otp,
#                 'masked_email': masked_email,
#                 'action': "register",
#                 'time': str(timezone.now())
#             }
#             request.session['verify_otp_data'] = verify_otp_data
#             sub = "Your VulnTech Account - One-Time Password (OTP)"
#             msg = f'''Dear {f_name},

# Greetings from VulnTech!

#     To ensure the security of your account, we are providing you with a one-time password (OTP) for authentication. Please use the following OTP to complete your login:

# OTP: {otp}

#     If you did not attempt to log in or requested this OTP, please contact our support team immediately.

#     Thank you for choosing VulnTech. We prioritize the safety and privacy of your account.

# Best Regards,
# VulnTech Support Team

# ---

# *Note: This is an automated message. Please refrain from replying directly. For assistance or inquiries, kindly connect with our dedicated support team at support@vulntech.com. Thank you.*
# '''
#             from_email = conf_settings.EMAIL_HOST_USER
#             to = [email]
#             try:
#                 send_mail(sub, msg, from_email, to)
#             except Exception as e:
#                 print(e)
#                 messages.error(request, "Something went wrong! please try again later")
#             return redirect('verify_otp')
#     else:
#         terms_pages = Terms_pages.objects.all()
#         siteDetail = site_detail.objects.all()
#         context = {
#             'terms_pages': terms_pages,
#             'siteDetail': siteDetail,
#         }
#         return render(request, 'registration/signup.html', context)


# def otpVerify(request): 
#     user_data = request.session.get('verify_otp_data')
    
#     if not user_data:
#         messages.error(request, "Something went wrong! please try again")
#         return redirect('index')
#     # Check expiration: if time exceeds 10 minutes, remove data.
#     if datetime.strptime(user_data['time'], "%Y-%m-%d %H:%M:%S.%f%z") + timezone.timedelta(minutes=10) < timezone.now():
#         request.session.pop('verify_otp_data', None)

#     if request.method == 'POST':
#         otp_1 = bleach.clean(request.POST.get('otp_1', ''))
#         otp_2 = bleach.clean(request.POST.get('otp_2', ''))
#         otp_3 = bleach.clean(request.POST.get('otp_3', ''))
#         otp_4 = bleach.clean(request.POST.get('otp_4', ''))
#         otp_5 = bleach.clean(request.POST.get('otp_5', ''))
#         combined_otp = f"{otp_1}{otp_2}{otp_3}{otp_4}{otp_5}"
        
#         if combined_otp == user_data['otp']:
#             if user_data['action'] == 'register':
#                 user = User.objects.create_user(
#                     first_name=user_data['first_name'],
#                     last_name=user_data['last_name'],
#                     username=user_data['username'],
#                     email=user_data['email'],
#                     mobile=to_python(user_data['mobile']),
#                     password=user_data['password']
#                 )
#                 user_login(request, user)
#                 masked_mobile = f"{user_data['mobile'][:3]}{'X'*5}{user_data['mobile'][-4:]}"
#                 sub = "Welcome to VulnTech - Your Account is Ready!"
#                 msg = f"""Dear {user_data['first_name']},

# We are delighted to welcome you to VulnTech!

# Your account has been successfully created, and you are now part of our learning community. VulnTech offers a diverse range of tutorials and video courses to help you expand your knowledge and skills.

# Key Features:
# - In-depth Tutorials
# - Expert-led Video Courses
# - Interactive Learning Resources

# To get started, simply log in with your registered mobile and password. 
# Mobile Number : {masked_mobile}
# Login Link  :  https://www.vulntech.com/accounts/login

# Thank you for choosing VulnTech. We are committed to providing you with valuable resources to support your learning journey.

# Best Regards,
# The VulnTech Team

# ---

# *Note: This is an automated message. Please refrain from replying directly. For assistance or inquiries, kindly connect with our dedicated support team at support@vulntech.com. Thank you.*
# """
#                 from_email = conf_settings.EMAIL_HOST_USER
#                 to = [user_data['email']]
#                 try:
#                     send_mail(sub, msg, from_email, to)
#                     request.session.pop('verify_otp_data', None)
#                 except Exception:
#                     messages.error(request, "Something went wrong! please try again later")
#                 return redirect('index')
            
#             elif user_data['action'] == 'ChangeMobile':
#                 try:
#                     request.user.mobile = to_python(user_data['mobile'])
#                     request.user.save()
#                     messages.success(request, "Mobile Changed Successfully")
#                     request.session.pop('verify_otp_data', None)
#                     user_logout(request, request.user)
#                     return redirect('login')
#                 except Exception:
#                     messages.error(request, "Error in Changing Mobile. Try again later")
#                     request.session.pop('verify_otp_data', None)
#                     return redirect("mobileChange")
                
#             elif user_data['action'] == 'ChangeEmail':
#                 try:
#                     request.user.email = user_data['email']
#                     request.user.save()
#                     messages.success(request, "Email Changed Successfully")
#                     request.session.pop('verify_otp_data', None)
#                     user_logout(request)
#                     return redirect('login')
#                 except Exception:
#                     messages.error(request, "Error in Changing Email. Try again later")
#                     request.session.pop('verify_otp_data', None)
#                     return redirect("emailChange")
#             elif user_data['action'] == 'ChangePass':
#                 try:
#                     request.user.set_password(user_data['password'])
#                     request.user.save()
#                     messages.success(request, "Password Changed Successfully")
#                     request.session.pop('verify_otp_data', None)
#                     user_logout(request)
#                     return redirect('login')
#                 except Exception as e:
#                     messages.error(request, "Error in Changing Password. Try again later")
#                     request.session.pop('verify_otp_data', None)
#                     return redirect("emailChange")
#         else:
#             messages.error(request, "Wrong otp entered.")
#             return redirect('verify_otp')
    
#     else:
#         terms_pages = Terms_pages.objects.all()
#         siteDetail = site_detail.objects.all()
#         context = {
#             'masked_email': user_data['masked_email'],
#             'terms_pages': terms_pages,
#             'siteDetail': siteDetail,
#         }
#         return render(request, 'registration/verifyotp.html', context)
    

# def resend_otp(request):
#     user_data = request.session.get('verify_otp_data')

#     if not user_data:
#         messages.error(request, "User registration details not found.")
#         return redirect('register')

#     new_otp = str(random.randint(10000, 99999))
#     user_data['otp'] = new_otp
#     request.session['verify_otp_data'] = user_data

#     sub = "Your VulnTech Account - One-Time Password (OTP)"
#     msg = f"""Dear {user_data['username']},

# Greetings from VulnTech!

#     To ensure the security of your account, we are providing you with a one-time password (OTP) for authentication. Please use the following OTP to complete your login:

# OTP: {new_otp}

#     If you did not attempt to log in or requested this OTP, please contact our support team immediately.

#     Thank you for choosing VulnTech. We prioritize the safety and privacy of your account.

# Best Regards,
# VulnTech Support Team

# ---

# *Note: This is an automated message. Please refrain from replying directly. For assistance or inquiries, kindly connect with our dedicated support team at support@vulntech.com. Thank you.*
# """
#     from_email = conf_settings.EMAIL_HOST_USER
#     to = [user_data['email']]
#     try:
#         send_mail(sub, msg, from_email, to)
#     except Exception:
#         messages.error(request, "Something went wrong! please try again later")
#     return JsonResponse({'success': True})


# @login_required(login_url="login")
# def profile(request):
#     terms_pages = Terms_pages.objects.all()
#     siteDetail = site_detail.objects.all()
#     context = {    
#         'siteDetail': siteDetail,
#         'terms_pages': terms_pages,
#     }
#     return render(request, 'registration/profile.html', context)


# class CustomPasswordResetView(PasswordResetView):
#     template_name = 'registration/forgot_pass.html'
    
#     def form_valid(self, form):
#         email = bleach.clean(form.cleaned_data['email'])
#         try:
#             user = User.objects.get(email=email)
#             user.password_reset_sent_at = timezone.now()
#             user.reset_link_valid = True
#             user.save()
#             return super().form_valid(form)
#         except User.DoesNotExist:
#             return super().form_valid(form)
        

# class CustomPasswordResetConfirmView(PasswordResetConfirmView):
#     template_name = 'registration/Passreset_s.html'
    
#     def form_valid(self, form):
#         response = super().form_valid(form)
#         if hasattr(self, 'user') and self.user is not None:
#             self.user.reset_link_valid = False
#             self.user.save()
#         else:
#             print("Not valid link set as false")
#         return response
    
#     def form_invalid(self, form):
#         combined_errors = list(form.non_field_errors()) + list(form['new_password1'].errors) + list(form['new_password2'].errors)
#         context = self.get_context_data(form=form, combined_errors=combined_errors)
#         return self.render_to_response(context)
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         terms_pages = Terms_pages.objects.all()
#         siteDetail = site_detail.objects.all()
#         if self.user.reset_link_valid:
#             now = timezone.now()
#             t = self.user.password_reset_sent_at + timezone.timedelta(minutes=30) > now
#             self.user.reset_link_valid = t
#             context['valid_link'] = t
#             context['terms_pages'] = terms_pages
#             context['siteDetail'] = siteDetail
#             self.user.save()
#         else:
#             context['valid_link'] = False
#             context['terms_pages'] = terms_pages
#             context['siteDetail'] = siteDetail
#         return context


# @login_required(login_url="login")
# def profile_view(request):
#     terms_pages = Terms_pages.objects.all()
#     siteDetail = site_detail.objects.all()
#     context = {
#         'terms_pages': terms_pages,
#         'siteDetail': siteDetail,
#     }
#     return render(request, 'registration/view_profile.html', context)


# @login_required(login_url="login")
# def profile_edit(request):
#     user = request.user

#     if request.method == 'POST':
#         try:
#             # Clean the input fields using bleach
#             user.first_name = bleach.clean(request.POST.get('first_name', ''))
#             user.last_name = bleach.clean(request.POST.get('last_name', ''))
#             user.username = bleach.clean(request.POST.get('username', ''))

#             if 'pic' in request.FILES:
#                 pic = request.FILES['pic']
#                 validate_image(pic)  # Validate the uploaded file

#                 # Convert image to PNG
#                 image = Image.open(pic)
#                 if image.format != 'PNG':
#                     image = image.convert('RGBA')  # Ensure compatibility with PNG
#                     buffer = BytesIO()
#                     image.save(buffer, format='PNG')
#                     buffer.seek(0)
#                     pic = InMemoryUploadedFile(
#                         buffer,  # File-like object
#                         'ImageField',  # Field name
#                         f"{user.id}_profile.png",  # File name
#                         'image/png',  # MIME type
#                         buffer.getbuffer().nbytes,  # File size
#                         None  # Charset
#                     )

#                 user.pic = pic

#             user.save()
#             messages.success(request, "Profile Updated Successfully")
#             return redirect('edit_profile')
#         except ValidationError as e:
#             messages.error(request, f"Error: {e.message}")
#             return redirect("edit_profile")
#         except Exception as e:
#             messages.error(request, f"Error in updating profile. Try again: {str(e)}")
#             return redirect("edit_profile")
#     else:
#         form = UserForm(instance=user)
#         countryCode = region_code_for_country_code(user.mobile.country_code)
#         terms_pages = Terms_pages.objects.all()
#         siteDetail = site_detail.objects.all()
#         context = {
#             'form': form,
#             'countryCode': countryCode,
#             'terms_pages': terms_pages,
#             'siteDetail': siteDetail,
#         }
#         return render(request, 'registration/edit_profile.html', context)


# @login_required(login_url="login")
# def settings(request):
#     terms_pages = Terms_pages.objects.all()
#     siteDetail = site_detail.objects.all()
#     context = {
#         'terms_pages': terms_pages,
#         'siteDetail': siteDetail,
#     }
#     return render(request, 'registration/settings.html', context)


# @login_required(login_url="login")
# def account_info(request):
#     terms_pages = Terms_pages.objects.all()
#     siteDetail = site_detail.objects.all()
#     context = {
#         'terms_pages': terms_pages,
#         'siteDetail': siteDetail,
#     }
#     return render(request, 'registration/account_info.html', context)


# @login_required(login_url="login")
# def delete_account(request):
#     request.user.delete()
#     user_logout(request) 
#     return redirect('index')


# @login_required(login_url="login")
# def mobileChange(request):
#     user = request.user

#     if request.method == 'POST':
#         mobile = request.POST.get('mobile')
#         mobile = to_python(mobile)

#         existing_mobile_user = User.objects.filter(mobile=mobile).first()
        
#         if not mobile.is_valid():
#             messages.error(request, "Invalid Mobile Number")
#             return redirect('mobileChange')
#         elif to_python(user.mobile) == mobile:
#             messages.info(request, "Retained the prior mobile number, no changes made.")
#             return redirect('mobileChange')
#         elif existing_mobile_user:
#             masked_email = f"{existing_mobile_user.email[:2]}{'X'*5}{existing_mobile_user.email[-13:]}"
#             messages.error(request, f"Hold on! Mobile Number is already linked to a ({masked_email}).")
#             return redirect('mobileChange')
#         else:
#             otp = str(random.randint(10000, 99999))
#             masked_email = f"{user.email[:2]}{'X'*5}{user.email[-13:]}"
#             verify_otp_data = {
#                 'mobile': str(mobile),
#                 'otp': otp,
#                 'masked_email': masked_email,
#                 'username': user.username,
#                 'action': "ChangeMobile",
#                 'time' : str(timezone.now())
#             }

#             request.session['verify_otp_data'] = verify_otp_data
            
                
#             sub = "Your VulnTech Account - One-Time Password (OTP)"
                
#             msg = f'''Dear {user.username},

# Greetings from VulnTech!

# You have initiated a mobile number change for your account. Please find your One-Time Password (OTP) below:

# OTP: {otp}

# If you did not request this change or are unsure about this activity, please contact our support team immediately.

# Thank you for choosing VulnTech. We prioritize the safety and privacy of your account.

# Best Regards,
# VulnTech Support Team

# ---

# *Note: This is an automated message. Please refrain from replying directly. For assistance or inquiries, kindly connect with our dedicated support team at support@vulntech.com. Thank you.*
# '''

#             from_email = conf_settings.EMAIL_HOST_USER
#             to = [user.email]
#             try:
#                 send_mail(sub, msg, from_email, to)
#             except Exception:
#                 messages.error(request,"Something went wrong! please try again later")
#             return redirect('verify_otp')
#     else: 
#         form = UserForm1(instance=user)
#         countryCode = region_code_for_country_code(user.mobile.country_code)
#         terms_pages = Terms_pages.objects.all()
#         siteDetail = site_detail.objects.all()
#         context = {
#             'form': form,
#             'countryCode' : countryCode,
#             'terms_pages' :terms_pages,
#             'siteDetail' : siteDetail,
#         }
#         return render(request, 'registration/mobileChange.html', context)

# @login_required(login_url="login")
# def emailChange(request):
#     user = request.user

#     if request.method == 'POST':
#         email = request.POST.get('email')
#         existing_email_user = User.objects.filter(email=email).first()
        
#         if existing_email_user:
#             masked_mobile = f"{str(existing_email_user.mobile)[:3]}{'X'*5}{str(existing_email_user.mobile)[-4:]}"
#             messages.info(request, f"Watch out! Email Address is connected to a ({masked_mobile}).")
#             return redirect('emailChange')
#         elif to_python(user.email) == email:
#             messages.info(request, "Retained the prior email, no changes made.")
#             return redirect('emailChange')
#         else:
#             otp = str(random.randint(10000, 99999))
#             masked_email = f"{email[:2]}{'X'*5}{email[-13:]}"
#             verify_otp_data = {
#                 'email': email,
#                 'otp': otp,
#                 'masked_email': masked_email,
#                 'username': user.username,
#                 'action': "ChangeEmail",
#                 'time' : str(timezone.now())
#             }

#             request.session['verify_otp_data'] = verify_otp_data
            
                
#             sub = "Your VulnTech Account - One-Time Password (OTP)"
                
#             msg = f'''Dear {user.username},

# Greetings from VulnTech!

# You have initiated a email id change for your account. Please find your One-Time Password (OTP) below:

# OTP: {otp}

# If you did not request this change or are unsure about this activity, please contact our support team immediately.

# Thank you for choosing VulnTech. We prioritize the safety and privacy of your account.

# Best Regards,
# VulnTech Support Team

# ---

# *Note: This is an automated message. Please refrain from replying directly. For assistance or inquiries, kindly connect with our dedicated support team at support@vulntech.com. Thank you.*
# '''

#             from_email = conf_settings.EMAIL_HOST_USER
#             to = [email]
#             try:
#                 send_mail(sub, msg, from_email, to)
#             except Exception:
#                 messages.error(request,"Something went wrong! please try again later")
#             return redirect('verify_otp')
        
#     else: 
#         form = UserForm1(instance=user)
#         terms_pages = Terms_pages.objects.all()
#         siteDetail = site_detail.objects.all()
#         context = {
#             'form': form,
#             'terms_pages' : terms_pages,
#             'siteDetail' : siteDetail
#         }
#         return render(request, 'registration/emailChange.html', context)



# class CustomPasswordChangeView(PasswordChangeView):
#     template_name = 'registration/PassChange.html'
#     success_url = reverse_lazy("verify_otp")

#     def form_valid(self, form):
#         user = self.request.user
#         otp = str(random.randint(10000, 99999))
#         masked_email = f"{user.email[:2]}{'X'*5}{user.email[-13:]}"
#         verify_otp_data = {
#             'password': form.cleaned_data['new_password1'],
#             'otp': otp,
#             'masked_email': masked_email,
#             'username': user.username,
#             'action': "ChangePass",
#             'time' : str(timezone.now())
#         }
#         self.request.session['verify_otp_data'] = verify_otp_data
        
#         # Compose and send OTP email
#         sub = "Your VulnTech Account - One-Time Password (OTP)"
#         msg = f'''Dear {user.username},

# Greetings from VulnTech!

# You have initiated a Password change for your account. Please find your One-Time Password (OTP) below:

# OTP: {otp}

# If you did not request this change or are unsure about this activity, please contact our support team immediately.

# Thank you for choosing VulnTech. We prioritize the safety and privacy of your account.

# Best Regards,
# VulnTech Support Team

# ---

# *Note: This is an automated message. Please refrain from replying directly. For assistance or inquiries, kindly connect with our dedicated support team at support@vulntech.com. Thank you.*
# '''
#         from_email = conf_settings.EMAIL_HOST_USER
#         to = [user.email]
#         try:
#             send_mail(sub, msg, from_email, to)
#         except Exception:
#             messages.error(self.request,"Something went wrong! please try again later")
            
#         # Continue with the default behavior
#         return super().form_valid(form)

#     def form_invalid(self, form):
#         combined_errors = list(form.non_field_errors()) + list(form['old_password'].errors) + list(form['new_password1'].errors) + list(form['new_password2'].errors)
#         terms_pages = Terms_pages.objects.all()
#         siteDetail = site_detail.objects.all()
#         context = self.get_context_data(form=form, combined_errors=combined_errors,terms_pages=terms_pages,siteDetail=siteDetail)
#         return self.render_to_response(context)
    
# @login_required(login_url="login")
# def support(request):
#     account_faq_category = account_FAQ_cate.objects.all().order_by('id')
#     account_faq = account_FAQ.objects.all()
#     terms_pages = Terms_pages.objects.all()
#     siteDetail = site_detail.objects.all()
#     context = {
#         'account_faq': account_faq,
#         'account_faq_category' : account_faq_category,
#         'terms_pages' : terms_pages,
#         'siteDetail' : siteDetail,
#     }
#     return render(request, 'registration/help&support.html', context)

# def custom_permission_denied_view(request, reason=""):
#     return render(request, '403_device_limit.html', {
#         "reason": reason
#     }, status=403)