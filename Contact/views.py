from django.shortcuts import render
from .models import Contact_Master
# Create your views here.

def contact(request):
    if request.method=="POST":
        username=request.POST['name']
        email=request.POST['email']
        mobile=request.POST['mob']
        feedback=request.POST['feedback']
        ob=Contact_Master.objects.create(Name=username,Email=email,Mobile=mobile,Feedback=feedback)
        ob.save()
        return render(request,"contact_details.html",{'MSG':'Successfully Submitted'})
    return render(request,"contact_details.html")




