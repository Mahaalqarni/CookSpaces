from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.models import User,Group
from django.contrib.auth import authenticate
from django.db import IntegrityError,transaction
from accounts.models import KitchenOwner
from .models import Kitchen,Equipment


def register_owner(request:HttpRequest):
    msg = None

    if request.method == "POST":
        try:

        
            with transaction.atomic():
                
                new_user = User.objects.create_user(
                    username=request.POST["username"],
                    email=request.POST["email"],
                    first_name=request.POST["first_name"],
                    last_name=request.POST["last_name"],
                    password=request.POST["password"]
                    )
                new_user.save()
                if not user.groups.filter(name='Kitchen_owner').exists():
                    group = Group.objects.get(name="Kitchen_owner")
                    user.groups.add(group)

                
                register_owner = KitchenOwner(
                    user=new_user,
                    commercial_register=request.FILES.get("commercial_register"),
                    avatar=request.FILES.get("avatar", KitchenOwner.avatar.field.get_default()),
                    phone=request.POST["phone"],
                    verified=request.POST.get("verified",False)
                    )
                register_owner.save()

                
            return redirect("accounts:login_user")
        
        except IntegrityError as e:
            msg = "This username is already taken. Please choose a different username."
            print(e)

        except Exception as e:
            msg = "Something went wrong. Please try again."
            print(e)
    

    return render(request, "KitchenOwner/register_owner.html", {"msg" : msg})


def owner_profile(request : HttpRequest):
    # owner = KitchenOwner.objects.get() 
    pass 

def update_profile(request :HttpRequest):
    pass 

def add_kitchen(request :HttpRequest,owner_id):
    
    equipments = Equipment.objects.all()
    
    if request.method == "POST":
        kitchen = Kitchen(
            kitchen_owner = KitchenOwner.objects.get(id=owner_id),
            title = request.POST["title"],
            desc = request.POST["desc"],
            poster = request.FILES.get("poster"),
            space = request.POST["space"],
            
            #py default False 
            has_ventilation = request.POST.get("has_ventilation", False),
            has_toilet = request.POST.get("has_toilet", False),
            has_storage = request.POST.get("has_storage", False),
            has_waitingarea = request.POST.get("has_waitingarea", False),
            price = request.POST["price"],
            #choices:
            loc_latitude = request.POST["loc_latitude"],
            loc_longitude = request.POST["loc_longitude"],
            period = request.POST.get("period"),
            status = "pending"
        )
        kitchen.save()
        kitchen.equipment.set(request.POST.getlist("equipments",[]))
        
    return render(request,"KitchenOwner/add_kitchen.html",{"period":Kitchen.periods.choices,"equipments":equipments,"owner_id":owner_id})


def update_kitchen(request :HttpRequest):
    pass 

def kitchen_details(request :HttpRequest,kitchen_id):
    kitchen=Kitchen.objects.get(id=kitchen_id)
    
    return render(request,"KitchenOwner/kitchen_details.html",{"kitchen":kitchen})
    

def my_orders(request :HttpRequest):
    pass 
