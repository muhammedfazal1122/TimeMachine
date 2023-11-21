from django.shortcuts import render,redirect
from django.contrib import messages
from django.views.decorators.cache import cache_control
from django.contrib.sessions.models import Session
from .models import Brand

# Create your views here.




@cache_control(no_cache=True,must_revalidate=True,no_store=True)   
def admn_brand_list(request):
    brand = Brand.objects.all()
    context={
        'brand':brand
    }
    return render(request, "evara-backend/page-brands.html",context)