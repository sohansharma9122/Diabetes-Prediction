from django.shortcuts import render
from Register.models import Register_Master

def signup(request):
    MSG = ""
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("pwd")
        mobile = request.POST.get("mobile")
        gender = request.POST.get("gender")
        dob = request.POST.get("dob")
        address = request.POST.get("addr")

        # check if email already exists
        if Register_Master.objects.filter(Email=email).exists():
            MSG = "This Email is already registered. Please login or use another email."
        else:
            Register_Master.objects.create(
                Name=name,
                Email=email,
                Password=password,
                Mobile=mobile,
                Gender=gender,
                DOB=dob,
                Address=address
            )
            MSG = "Registration Successful!"

    return render(request, "signup.html", {"MSG": MSG})
