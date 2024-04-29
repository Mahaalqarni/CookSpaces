from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate
from django.db import IntegrityError,transaction
from accounts.models import KitchenOwner,Renter,Chife

def register_renter(request:HttpRequest):
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

                if not new_user.groups.filter(name='Renter').exists():
                    group = Group.objects.get(name="Renter")
                    new_user.groups.add(group)

                register_renter = Renter(
                    user=new_user, 
                    about=request.POST["about"],
                    avatar=request.FILES.get("avatar", KitchenOwner.avatar.field.get_default()),
                    phone=request.POST["phone"]
                    )
                register_renter.save()

            return redirect("accounts:login")
        
        except IntegrityError as e:
            msg = "This username is already taken. Please choose a different username."
            print(e)

        except Exception as e:
            msg = "Something went wrong. Please try again."
            print(e)
    
    return render(request, "renters/register_renter.html", {"msg" : msg})

def profile(request:HttpRequest):
    
    return render(request, 'renters/profile.html')


def my_order(request:HttpRequest):
    
    return render(request, 'renters/my_order.html')

def booking(request:HttpRequest):
    
    return render(request, 'renters/booking.html')

def saved_kitchens(request:HttpRequest):
    
    return render(request, 'renters/saved_kitchens.html')