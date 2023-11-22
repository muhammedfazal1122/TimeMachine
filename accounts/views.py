from django.shortcuts import render,redirect,HttpResponse,get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from .forms import RegistrationForm
from .models import Account
from django.views.decorators.cache import cache_control
from django.contrib.sessions.models import Session
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from .models import Account
import pyotp
from product.models import Product
import re
# varification
# views.py
from django.core.mail import send_mail
import random
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model


# ------------------------------------------#forgot password#------------------------------

from django.utils.http import  urlsafe_base64_decode


# Create your views here.


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@csrf_protect
def user_login(request):
    if request.user.is_authenticated:
        return redirect('/')
    
    if request.method == "POST":
        email =request.POST['email']
        password = request.POST['password']

        if not Account.objects.filter(email=email).exists():
            messages.error(request, "Invalid Email Adress")
            return redirect('accounts:user-login')
        
        if not Account.objects.filter(email=email,is_active=True).exists():
            messages.error(request, "You are blocked by admin ! Please contact admin ")
            return redirect('accounts:user-login') 

        user=authenticate(request,email=email,password=password)

        if user:
            request.session.create()
            print('session key is:',request.session.session_key)
            request.session['email'] = email
            return redirect('accounts:sent-otp')
        else:
            messages.error(request, "Invalid credentials")
            return redirect('accounts:user-login')
        
    return render (request,'evara-frontend/accounts/login.html')

User = get_user_model()  # Get the User model defined in your project


def sent_otp(request):
   random_num=random.randint(1000,9999)
   print("OOTTTPPP::",random_num)
   request.session['OTP_Key']=str(random_num)
   send_mail(
   "OTP AUTHENTICATING TimeMachine",
   f"{random_num} -OTP",
   "ecomm.apps.info@gmail.com",
   [request.session['email']],
   fail_silently=False,
    )
   return redirect('accounts:verify-otp')

from django.contrib import messages
from django.contrib.auth import login

def verify_otp(request):
    print(request.session.get('email'))
    try:
        user=Account.objects.get(email=request.session['email'])
    except:
        pass
    stored=request.session['OTP_Key']
    print(stored,user, type(stored))
    if request.method =='POST':
        entered=request.POST.get('otp')
        if stored==entered:
            login(request,user)
            messages.success(request, "Login successful!")
            return redirect('app:index')
        else:
            messages.warning(request, "Invalid OTP!")
            return redirect('accounts:verify-otp')
    return render(request,'evara-frontend/otp.html')



def resend_otp(request):
   print("###########################################")
   random_num=random.randint(1000,9999)
   request.session['OTP_Key']=str(random_num)
   send_mail(
   "OTP AUTHENTICATING TimeMachine",
   f"{random_num} -OTP",
   "ecomm.apps.info@gmail.com",
   [request.session['email']],
   fail_silently=False,
    )
   messages.success(request, "OTP has been resent successfully!")
   return redirect('accounts:verify-otp')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def register(request):
    if request.user.is_authenticated:
        return redirect('app:index')

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirmpassword = request.POST['password2']

        # Check for white spaces in username, password, and email
        if any(char.isspace() or re.match('[@#$%^@%@#%&]', char) for char in username):
            messages.error(request, "Username contains invalid characters")
        # elif any(char.isspace() or re.match('[@#$%^@%@#%&]', char) for char in password):
        #     messages.error(request, "e Must be Letter")
        elif any(char.isspace() or re.match('[#$%^%&]', char) for char in email):
            messages.error(request, "Invalid email format")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email is Already taken")
        elif password != confirmpassword:
            messages.error(request, "Please make sure passwords match")
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, "Registration successful")
            return redirect('accounts:user-login')
    
    return render(request, "evara-frontend/accounts/register.html")



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def user_logout(request):
    request.session.flush()
    logout(request)
    messages.success(request, "You have been logged out")
    return redirect('accounts:user-login')

def forgotpassword(request):
    return render(request,"evara-frontend/accounts/forgotpassword.html")





########################## admin   ####################################


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_login(request):
    if request.method == "POST":        
        print(request.POST)
        email = request.POST.get('email')  # Use request.POST.get to safely access POST data
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)

        if user and user.is_superuser:
            login(request, user)
            messages.success(request, "Admin login successful!")
            return redirect('accounts:admin_dashboard')
        else:
            messages.warning(request, "Invalid admin credentials!")

    return render(request, 'evara-backend/page-account-login.html')



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='accounts:admin_login')  # Use the named URL pattern
def admin_dashboard(request):

    return render(request,'evara-backend/index.html')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def admin_logout(request):
    # if 'email' in request.session:
    #     del request.session['email']
    logout(request)
    messages.info(request,"Logout Successfully")
    return render(request, 'evara-backend/page-account-login.html')   