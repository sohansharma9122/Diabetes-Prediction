from django.shortcuts import render, redirect
from Register.models import Register_Master
from django.contrib.auth.models import User

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

        # split name into first & last
        name_parts = name.split()
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        # check if already exists
        if Register_Master.objects.filter(Email=email).exists():
            MSG = "This Email is already registered. Please login or use another email."

        else:
            # ✅ SAVE IN YOUR CUSTOM TABLE (unchanged)
            Register_Master.objects.create(
                Name=name,
                Email=email,
                Password=password,
                Mobile=mobile,
                Gender=gender,
                DOB=dob,
                Address=address
            )

            # ✅ ALSO SAVE IN DJANGO AUTH TABLE
            User.objects.create_user(
                username=email,   # email as username
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            MSG = "Registration Successful!"

    return render(request, "signup.html", {"MSG": MSG})