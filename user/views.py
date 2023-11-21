from django.shortcuts import render
from django.shortcuts import render,redirect,HttpResponse,get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from accounts.models import Account
from .models import AdressBook
import re
from product.models import Product
# Create your views here.



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
