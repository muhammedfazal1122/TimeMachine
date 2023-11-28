
from django.shortcuts import render, redirect,reverse,get_object_or_404
from django.http import HttpResponse
from django.http import JsonResponse
import datetime
import random
import string
from django.views import View
from order.models import Coupon,Coupon_Redeemed_Details
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from datetime import date, datetime
import datetime
from cart.models import CartItem
from .forms import OrderForm
from .models import Order,OrderProduct,Payment
from product.models import Variation 
from user.models import AdressBook
from category.models import Category
from django.http import HttpResponseRedirect
import razorpay
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.contrib import messages
from django.utils import timezone
# from datetime import datetime, timedelta
from django.db.models import Sum

# Create your views here.







def cancel_order(request,order_id):
    
    order = get_object_or_404(Order, id=order_id)
    if order.status=="Pending" or "Shipped":
        order.status = "Cancelled"
        order.save()
   
    return redirect("orders:my_orders") 


def update_status(request):
    if request.method=="POST":
        order_id = request.POST.get('OrderID')
        status = request.POST.get('status')
        order = get_object_or_404(Order, id=order_id)

        # Update the order status
        order.status = status
        order.save()
        print(order.status,order.order_number)
    return redirect('orders:admn_product_order')  



@login_required(login_url='accounts:user-login')
def order_placed(request, total=0, quantity=0):
    if not request.user.is_authenticated:
        return redirect('app:index')


    current_user = request.user

    # If the cart count is less than 0, then redirect back to home
    cart_items = CartItem.objects.filter(user=current_user)
 

    grand_total = 0
    tax = 0


    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
        if cart_item.variations:
            variation_value = cart_item.variations.variation_value


    tax = (2 * total) / 100

    grand_total = total + tax
    
    



    if request.method == 'POST':
        selected_payment_option = request.POST.get('payment_option')
        coupon=request.POST.get('coupon')
        total_final=request.POST.get('total_final')
        if coupon :
            grand_total = total_final
            total = total_final

            print("rrrrrrrrrrrrrrrrrrrr",total_final,coupon,grand_total)
        
        try:
            address = AdressBook.objects.get(user=request.user, is_default=True)
        except AdressBook.DoesNotExist:
            messages.warning(request, 'No delivery address exists! Add an address and try again')
            return redirect('cart:checkout')

        data = Order()
        data.user = current_user
        data.first_name = address.first_name
        data.last_name = address.last_name
        data.phone = address.phone
        data.email = address.email
        data.address_line_1 = address.address_line_1
        data.city = address.city
        data.state = address.state
        data.country = address.country
        data.pincode = address.pincode
        data.order_total = grand_total
        data.total = total
        data.tax = tax
        data.ip = request.META.get('REMOTE_ADDR')
        data.save()

        # Generate order number
        yr = int(datetime.date.today().strftime('%Y'))
        dt = int(datetime.date.today().strftime('%d'))
        mt = int(datetime.date.today().strftime('%m'))
        d = datetime.date(yr, mt, dt)
        current_date = d.strftime("%Y%m%d")
        order_number = current_date + str(data.id)
        data.order_number = order_number
        data.is_ordered = True
        data.save()

        payment_id = f'uw{data.order_number}{data.id}'
        payment = Payment.objects.create(
            user=current_user, 
            payment_method='Cash on Delivery',
            payment_id=payment_id,
            amount_paid=data.order_total,
            status='COMPLETED' )
        payment.save()
        data.payment=payment
        data.save()

        ordered_products = []

        # Create ordered products
        # Create ordered products
        for cart_item in cart_items:
            # Check if the cart item has a variation
            if cart_item.variations:
                # Note: Assuming that variations is a ForeignKey in CartItem
                variation = cart_item.variations
                ordered_product = OrderProduct.objects.create(
                    user=current_user,
                    order=data,
                    payment=payment,
                    product=cart_item.product,
                    product_price=cart_item.product.price,
                    quantity=cart_item.quantity,
                    is_ordered=True,
                )
                # Assign the variation value to the OrderProduct
                ordered_product.variations.add(variation)
                ordered_product.save()
                ordered_products.append(ordered_product)
            else:
                # If no variation, create a single OrderProduct without variations
                ordered_product = OrderProduct.objects.create(
                    user=current_user,
                    order=data,
                    payment=payment,
                    product=cart_item.product,
                    product_price=cart_item.product.price,
                    quantity=cart_item.quantity,
                    is_ordered=True,
                )
                ordered_products.append(ordered_product)

        # Remove cart items after ordering
        cart_items.delete()
        context = {
            'order': data,
            'cart_items': cart_items,
            'total': total,
            'tax': tax,
            'grand_total': grand_total,
            'ordered_products':ordered_products,

        }

        if selected_payment_option == "CashOnDelivery":
            print("Selected Payment Method:", selected_payment_option)

            return render(request, "evara-frontend/order_placed.html", context)

        elif selected_payment_option == "RAZORPAY":

            payment_id = f'uw{data.order_number}{data.id}'
            payment = Payment.objects.create(
            user=current_user, 
            payment_method='Razorpay',
            payment_id=payment_id,
            amount_paid=data.order_total,
            status='Pending' )
            payment.save()
            data.payment=payment
            data.save()
            return render(request, "evara-frontend/online_payment.html", context)
   
    return redirect("cart:checkout")                                   



def online_payment(request):
    current_user = request.user
    payment_method = request.GET.get('method')
    payment_id = request.GET.get('payment_id')
    # payment_order_id = request.GET.get('payment_order_id')
    order_id = request.GET.get('order_id')


  
    if not current_user.is_authenticated:
        return HttpResponse("User must be logged in for online payment")

    # Get order details
    try:
        order = Order.objects.get(order_number=order_id, user=current_user)
    except Order.DoesNotExist:
        return HttpResponse("Order not found")

    # Get ordered products for the order
    ordered_products = OrderProduct.objects.filter(order=order)

    # Calculate total amount (you might need to adjust this based on your models)
    total_amount = order.order_total

    # You can pass additional context data if needed
    context = {
        'order': order,
        'ordered_products': ordered_products,
        'total_amount': total_amount,
        'payment_method':payment_method,
        'payment_id':payment_id,
        # 'payment_order_id':payment_order_id,
        

    }

    return render(request, "evara-frontend/order_placed.html", context)



    
    


def ordered_product_detailes(request, order_id):
    current_user = request.user

    try:
        order = Order.objects.get(id=order_id, user=current_user)
    except Order.DoesNotExist:
        # Handle the case where the order does not exist
        # You can redirect or show an error message
        return HttpResponse("Order not found")

    ordered_products = OrderProduct.objects.filter(order=order)

    context = {
        'order': order,
        'ordered_products': ordered_products,

    }
    return render(request, 'evara-frontend/ordered_product_detailes.html', context)





@login_required(login_url='accounts:user-login')
def my_orders(request):

    if not request.user.is_authenticated:
        return redirect('app:index')
    
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    order_products = OrderProduct.objects.filter(order__in=orders)
    context = {
        'orders': orders,
        "order_products":order_products
    }
  
    return render(request, 'evara-frontend/order.html', context)







#-------------------------------------------ADMIN---------------------------------------------------#


def admn_product_order(request):
    orders = Order.objects.all().order_by("-created_at")
    order_products = OrderProduct.objects.filter(order__in=orders)
    categories = Category.objects.all()
    context = {
        'orders': orders,
        "order_products":order_products,
        "categories":categories,
    }
  

    return render(request,"evara-backend/page-orders-detail.html",context)



#-------------------------------------------COUPONSSSSSS---------------------------------------------------#


class AdmnCouponManagementView(View):
    template_name = "evara-backend/admin-coupon-management.html"

    def get(self, request, *args, **kwargs):
        coupons = Coupon.objects.all()
        context = {
            'coupons': coupons,
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        coupon_code = request.POST.get("couponcode")
        discount_amount = request.POST.get("discount")
        minimum_amount = request.POST.get("minimumAmount")
        valid_to = request.POST.get("couponexpiry")


        # Check if a coupon with the same code already exists
        if Coupon.objects.filter(coupon_code=coupon_code).exists():
            messages.warning(request,"Coupon Code is Alredy Exist")
            coupons = Coupon.objects.all()
            return render(request, self.template_name, {"coupons": coupons, "error": "Duplicate coupon code"})

        coupon = Coupon.objects.create(
            coupon_code=coupon_code,
            discount_amount=discount_amount,
            minimum_amount=minimum_amount,
            valid_to=valid_to
        )
        


        coupons = Coupon.objects.all()
        # Render the same template with the updated list of coupons
        return redirect("orders:admn_coupon_management")
    


def generate_code(request):
  alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits
  code = ''.join(random.choice(alphabet) for i in range(8))
  return JsonResponse({'code': code})


def delete_coupon(request,id):
    
    coupon = get_object_or_404(Coupon, id=id)
    coupon.delete()
    return redirect("orders:admn_coupon_management") 






def apply_coupon(request):
    if request.method == "POST":
        coupon_code = request.POST.get("couponCode")
        total = request.POST.get("total")
        user = request.user

        try:
            coupon = Coupon.objects.get(coupon_code=coupon_code, valid_to__gte=timezone.now())
            print("ffffffffffffffffffffffffffffff")
            if coupon.Is_Redeemed_By_User_New(request,user):
                print("gggggggggggggggggggggggggggggg")

                messages.warning(request,"User Already Used The Coupon")
                return redirect('cart:checkout')
            else:
                if not coupon.Is_Redeemed_By_User_New(request,user):
                    # If not redeemed yet, save the redemption details
                    new_redeemed_detail = Coupon_Redeemed_Details(coupon=coupon, user=user)
                    new_redeemed_detail.save()
                print("mmmmmmmmmmmmmmmmmmmmmmmm")

                return JsonResponse( {'success': True, 'coupon': coupon.discount_amount} )
        except Coupon.DoesNotExist:
            messages.warning(request, 'Invalid coupon code or expired.')
            return redirect('cart:checkout')
        except Exception as e:
            print("Error applying coupon:", e)
            # Handle the exception appropriately or provide a fallback response
            return redirect('cart:checkout')

    return redirect('cart:checkout')

