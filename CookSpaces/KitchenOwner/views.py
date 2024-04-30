from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.models import User,Group
from django.contrib.auth import authenticate
from django.db import IntegrityError,transaction
from accounts.models import KitchenOwner,Renter
from main.models import Review
from Renters.models import BookMark
from .models import Kitchen,Equipment
from Renters.models import Order


#kitchen owner register:
def register_owner(request:HttpRequest):
    msg = None

    if request.method == "POST":
        try:

        
            with transaction.atomic():
                
                user = User.objects.create_user(
                    username=request.POST["username"],
                    email=request.POST["email"],
                    first_name=request.POST["first_name"],
                    last_name=request.POST["last_name"],
                    password=request.POST["password"]
                    )
                user.save()
                if not user.groups.filter(name='Kitchen_owner').exists():
                    group = Group.objects.get(name="Kitchen_owner")
                    user.groups.add(group)

                
                register_owner = KitchenOwner(
                    user=user,
                    commercial_register=request.FILES.get("commercial_register"),
                    avatar=request.FILES.get("avatar", KitchenOwner.avatar.field.get_default()),
                    phone=request.POST["phone"],
                    verified=request.POST.get("verified",False)
                    )
                register_owner.save()

                
            return redirect("accounts:login")
        
        except IntegrityError as e:
            msg = "This username is already taken. Please choose a different username."
            print(e)

        except Exception as e:
            msg = "Something went wrong. Please try again."
            print(e)
    

    return render(request, "KitchenOwner/register_owner.html", {"msg" : msg})

#kitchen owner profile:
def owner_profile(request : HttpRequest,owner_username):
    owner = KitchenOwner.objects.get(user__username=owner_username) 
    
    return render(request,"KitchenOwner/owner_profile.html",{"owner":owner})
    
#kitchen owner update profile:
def update_owner_profile(request :HttpRequest,owner_username):
    owner = KitchenOwner.objects.get(user__username=owner_username) 
    msg=""
    if request.method == "POST":
        try:
            with transaction.atomic():
                user = owner.user
                user.email = request.POST["email"]
                user.save()
                
                owner.commercial_register = request.FILES.get("commercial_register")
                owner.avatar = request.FILES.get("avatar",owner.avatar)
                owner.phone = request.POST["phone"]
                owner.save()
                return redirect("KitchenOwner:owner_profile",owner_username)
            
        except Exception as e :
            msg = f"something went wrong !{e.__class__} "
    
    return render(request,"KitchenOwner/update_owner_profile.html",{"owner":owner,"msg":msg})

def add_kitchen(request :HttpRequest):
    
    equipments = Equipment.objects.all()
    
    if request.method == "POST":
        
        lat =  float(request.POST["loc_latitude"])
        lng = float(request.POST["loc_longitude"])
        kitchen = Kitchen(
            kitchen_owner = request.user.kitchenowner,
            title = request.POST["title"],
            desc = request.POST["desc"],
            image = request.FILES.get("poster", Kitchen.image.field.default),
            space = request.POST["space"],
            
            #py default False 
            has_ventilation = request.POST.get("has_ventilation", False),
            has_toilet = request.POST.get("has_toilet", False),
            has_storage = request.POST.get("has_storage", False),
            has_waitingarea = request.POST.get("has_waitingarea", False),
            price = request.POST["price"],
            is_negotiable =request.POST["is_negotiable"],
            loc_latitude = lat,
            loc_longitude = lng,
            city = request.POST.get("city"),
            period = request.POST.get("period"),
            status = "pending"
        )
        kitchen.save()
        kitchen.equipment.set(request.POST.getlist("equipments",[]))
        
    return render(request,"KitchenOwner/add_kitchen.html",{"period":Kitchen.periods.choices,"equipments":equipments,"city":Kitchen.cities.choices})

def update_kitchen(request :HttpRequest):
    pass 

def kitchen_details(request :HttpRequest,kitchen_id):
    try:
        #getting a kitchen detail
        kitchen = Kitchen.objects.get(pk=kitchen_id)
        reviews = Review.objects.filter(kitchen=kitchen)
        is_saved = request.user.is_authenticated and  BookMark.objects.filter(user=request.user, kitchen=kitchen).exists()
    except Kitchen.DoesNotExist:
        return render(request, "404.html")
    except Exception as e:
        print(e)
        
    return render(request, "kitchenowner/kitchen_details.html", {"kitchen" : kitchen, "reviews" : reviews, "is_saved" : is_saved})
        
def all_kitchens(request :HttpRequest):
    kitchens = Kitchen.objects.all()
    
    return render(request,"KitchenOwner/all_kitchens.html",{"kitchens":kitchens})

def rental_request(request : HttpRequest,kitchen_id):
    kitchen=Kitchen.objects.get(id=kitchen_id)
    renter =Renter.objects.get(user__id=request.user.id)
    if request.method =="POST":
        order = Order(
            renter = renter,
            kitchen=kitchen,
            start_date = request.POST["start_date"],
            end_date=request.POST["end_date"],
            note = request.POST["note"],
            status="pending"
        )
        order.save()
        msg="Your request was successfully sent!"
        
    return render(request,"kitchenowner/kitchen_details.html",{"kitchen":kitchen,"msg":msg})


def owner_orders(request :HttpRequest,owner_id):
    orders = Order.objects.filter(kitchen__kitchen_owner__user__id=owner_id)
    
    return render (request,"KitchenOwner/owner_orders.html",{"orders":orders})

def reject_order(request:HttpRequest,order_id):
    order = Order.objects.get(id=order_id)
    owner_id = order.kitchen.kitchen_owner.user.id
    order.status = "rejected"
    order.save()
    return redirect("KitchenOwner:owner_orders",owner_id)

def accept_order(request : HttpRequest, order_id):
    order = Order.objects.get(id=order_id)
    owner_id = order.kitchen.kitchen_owner.user.id
    order.status = "accepted"
    order.save()
    return redirect("KitchenOwner:owner_orders",owner_id)

def order_details(request : HttpRequest,order_id):
    order = Order.objects.get(id=order_id)

    return render(request,"KitchenOwner/order_details.html",{"order":order})