from django.shortcuts import render
from django.shortcuts import render,redirect,HttpResponse,get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from accounts.models import Account
from .models import AdressBook
from datetime import datetime  # Make sure to import datetime from the correct module
from product.models import Product
# Create your views here.
from django.shortcuts import render, redirect,get_object_or_404
from django.http import JsonResponse
import datetime
from django.contrib import messages
from django.conf import settings
from datetime import date, datetime
import datetime
from order.models import Order
from user.models import AdressBook
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta



def edit_profile(request):
    if not request.user.is_authenticated:
        return redirect('account:index')

    user_profile = Account.objects.get(email=request.user.email) # Get the UserProfile instance for the logged-in user

    if request.method == 'POST':
        # Handle the form submission and update the user details
        username = request.POST.get('username')
        # email = request.POST.get('email')
        email = request.POST.get('email')
        # password = request.POST.get('password')
        # Update the user profile fields with the form data
        user_profile.email = email
        # user_profile.password = password
        user_profile.username = username

        # Save the changes to the UserProfile and User models
        user_profile.save()
        messages.success(request,"updated sucesessfully")
        return redirect('app:index')  # Redirect to the user profile page after successful update
    else:
        return render(request, 'evara-frontend/edit-profile.html', {'user_profile': user_profile})








def manage_address(request):
    if not request.user.is_authenticated:
        return redirect('app:index')
    
    user = request.user
    addresses = AdressBook.objects.filter(user=user)
    default_address = addresses.filter(is_default=True).first()

    context = {
        'addresses': addresses,
        'default_address': default_address
    }
    return render(request, 'evara-frontend/manage-address.html', context)



def add_address(request):
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('account:index')
   
        address_line_1 = request.POST.get('address')
        address_line_2 = request.POST.get('address_line_2')
        country = request.POST.get('country')
        state = request.POST.get('state')
        city = request.POST.get('city')
        pincode = request.POST.get('pincode')
        phone = request.POST.get('phone')



        #Create a new shipping address instance
        address = AdressBook(user=request.user,   phone=phone, address_line_1=address_line_1, address_line_2=address_line_2, country=country, state=state, city=city, pincode=pincode)
        address.save()
        


        # Set is_default attribute of the newly added address and reset previous default
        if request.user.is_authenticated:
            AdressBook.objects.filter(user=request.user, is_default=True).update(is_default=False)
            address.is_default = True
            address.save()

        # if 'source' in request.GET and request.GET['source'] == 'checkout':
        #     # If the source is 'checkout', redirect back to the checkout page
        #     return redirect('user:checkout')  # Replace 'checkout' with your actual checkout view name

        return redirect('user:manage_address')
        
    else:
        return render(request, 'evara-frontend/add-adddres.html')
    

def delete_address(request, address_id):
    if not request.user.is_authenticated:
        return redirect('app:index')
    
    try:
        address = AdressBook.objects.get(id=address_id)
        address.delete()
    except AdressBook.DoesNotExist:
        pass

    return redirect('user:manage_address')



def edit_address(request, address_id):

    if not request.user.is_authenticated:
        return redirect('app:index')
    
    address = get_object_or_404(AdressBook, pk=address_id)

    if request.method == 'POST':
        # Handle the form submission and update the address details

        address.address_line_1 = request.POST.get('address_line_1')
 
        address.city = request.POST.get('city')
        address.state = request.POST.get('state')
        address.country = request.POST.get('country')
        address.pincode = request.POST.get('pincode')
        address.phone = request.POST.get('phone')
        address.save()

        return redirect('user:manage_address')  # Redirect to the address page after successful update

    return render(request, 'evara-frontend/edit-address.html', {'address': address})





def get_names(request):
    search = request.GET.get('search')
    
    # Check if 'search' is not None or empty
    if search:
        objs = Product.objects.filter(product_name__istartswith=search)
        payload = [{'name': obj.product_name} for obj in objs]
    else:
        payload = []

    return JsonResponse({
        'status': True,
        'payload': payload
     })





def admn_sales_report(request):
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    status_filter = int(request.GET.get('status_filter', 0))
    current_date = timezone.now().strftime("%Y-%m-%d")
    orders = []
    print(start_date,end_date,status_filter)


    if  is_valid_date(start_date) and is_valid_date(end_date) and status_filter ==  0:
    
        orders = Order.objects.all().order_by("-created_at")
        
    elif( not is_valid_date(start_date) )  and ( not is_valid_date(end_date)) and (status_filter ==  0):
        orders = filter_order_by_date( request,start_date, end_date)
    else:

        orders = filter_order_by_date_and_status( start_date, end_date, status_filter)

    context = {
        'start_date': start_date,
        'end_date': end_date,
        'status_filter': status_filter,
        'orders': orders,
        'current_date': current_date,

    }
    print(start_date,end_date,status_filter)
    return render(request, "evara-backend/sales-report.html", context)



def filter_order_by_date( request, start_date_str, end_date_str):
    start_date = convert_string_to_date(start_date_str)
    end_date = convert_string_to_date(end_date_str)

    if start_date > end_date:
        messages.warning(request, 'Start Date Must Be Less Than End Date')
        return Order.objects.all().order_by("-created_at")
    elif start_date == end_date:
        return Order.objects.filter(created_at__date=start_date).order_by("-created_at")
    else:
        return Order.objects.filter(created_at__date__range=(start_date, end_date)).order_by("-created_at")

def filter_order_by_date_and_status( start_date_str, end_date_str, status_filter):
    if not start_date_str or start_date_str == 'null' or not end_date_str or end_date_str == 'null':
        return filter_order_by_status(status_filter)

    start_date = convert_string_to_date(start_date_str)
    end_date = convert_string_to_date(end_date_str)

    if start_date == end_date:
        
        status = get_order_status_by_value(status_filter)
        return Order.objects.filter(created_at__date=start_date, status=status).order_by("-created_at") 
    else:
        status = get_order_status_by_value(status_filter)
        return Order.objects.filter(created_at__date__range=(start_date, end_date), status=status).order_by("-created_at") 

def filter_order_by_status(status_filter):
    status = get_order_status_by_value(status_filter)

    return Order.objects.filter(status=status).order_by("-created_at") 

def get_order_status_by_value(status_filter):
    # Implement your logic to map status_filter values to actual order statuses
    # Example: 
    if status_filter == 1:                    
        return "Pending"
    elif status_filter == 2:
        return "Shipped"
    elif status_filter == 3:
        return "Deliverd"
    elif status_filter == 4:
        return "Cancelled"
    elif status_filter == 5:
        return "Returned"
    # Add more mappings as needed

def convert_string_to_date(date_str):
    if not date_str or date_str == 'null':
        return date.today()
    return datetime.strptime(date_str, '%Y-%m-%d').date()


def is_valid_date(date_str):
    if not date_str or date_str == 'null':
        return True
    try:
        # Use the full module path for strptime
        datetime.strptime(date_str, '%Y-%m-%d')
        return False
    except ValueError:
        return True
