
from django.shortcuts import render, redirect,reverse,get_object_or_404
from django.http import HttpResponse
from django.http import JsonResponse
import datetime
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from datetime import datetime
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
    tax = (2 * total) / 100

    grand_total = total + tax
    



    if request.method == 'POST':
        selected_payment_option = request.POST.get('payment_option')

        
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
        for cart_item in cart_items:
            ordered_product = OrderProduct.objects.create(

                user=current_user,
                order=data,
                payment=payment,
                product=cart_item.product,
                product_price=cart_item.product.price,
                quantity=cart_item.quantity,
                is_ordered=True,

            )
            ordered_product.save()
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


def admn_sales_report(request):
    startDate = request.GET.get('startDate', None)
    endDate = request.GET.get('endDate', None)
    statusFilter = int(request.GET.get('StatusFilter', 0))

    if startDate and endDate and statusFilter == 0:
        orders = Order.objects.all().order_by('-created_at')
    elif statusFilter == 0:
        orders = Order.objects.filter(created_at__gte=startDate, created_at__lte=endDate).order_by('-created_at')
    # else:
    #     orders = Order.objects.filter(created_at__gte=startDate, created_at__lte=endDate, status=statusFilter).order_by('-created_at')


    context = {
        'StartDate': startDate,
        'EndDate': endDate,
        'StatusFilter': statusFilter,
        # 'OrderMainList': orders,
    }
    # order_products = OrderProduct.objects.filter(order__in=orders)
    context = {
        'orders': orders,
        # "order_products":order_products,
    }

    return render(request,"evara-backend/sales-report.html",context)


def get_weekly_sales():
    end_date = timezone.now()
    start_date = end_date - timezone.timedelta(days=7)

    return OrderProduct.objects.filter(
        order__created_at__range=(start_date, end_date)
    ).values('product__product_name').annotate(weekly_sales=Sum('quantity'))



def get_monthly_sales():
    end_date = timezone.now()
    start_date = end_date - timezone.timedelta(days=30)

    return OrderProduct.objects.filter(
        order__created_at__range=(start_date, end_date)
    ).values('product__product_name').annotate(monthly_sales=Sum('quantity'))



def get_yearly_sales():
    end_date = timezone.now()
    start_date = end_date - timezone.timedelta(days=365)


    return OrderProduct.objects.filter(
        order__created_at__range=(start_date, end_date)
    ).values('product__product_name').annotate(yearly_sales=Sum('quantity'))



def sales_report(request):
    weekly_sales_data = list(get_weekly_sales().values('product__product_name','weekly_sales'))  # Convert QuerySet to a list of dictionaries
    monthly_sales_data = list(get_monthly_sales().values('product__product_name','monthly_sales'))
    yearly_sales_data = list(get_yearly_sales().values('product__product_name','yearly_sales'))
    sales_data = {
        'weekly_sales': weekly_sales_data,
        'monthly_sales': monthly_sales_data,
        'yearly_sales': yearly_sales_data,
    }
    return JsonResponse(sales_data, safe=False)