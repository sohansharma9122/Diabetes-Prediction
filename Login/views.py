from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login

from django.contrib.auth.models import User
from Register.models import Register_Master
from django.contrib.auth.hashers import make_password

def login(request):
    msg = ""

    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()

        # ⚠️ IMPORTANT: password lena padega
        password = request.POST.get('password', '').strip()

        # authenticate using email as username
        user = authenticate(request, username=email, password=password)

        if user is not None:
            auth_login(request, user)   # ✅ Django login

            # OPTIONAL: keep your session also (no break)
            request.session['Name'] = user.first_name
            request.session['Email'] = user.email

            return redirect('home')
        else:
            msg = "Invalid Email or Password!"

    return render(request, "login.html", {'msg': msg})






def forget_password(request):
        MSG = ""
        if request.method == "POST":
            email = request.POST.get("email")
            new_pwd = request.POST.get("new_pwd")

            try:
                # 1. Django Auth Table (username = email)
                # Filter use karna zyada safe hai check karne ke liye
                user_query = User.objects.filter(username=email)
                
                if user_query.exists():
                    user = user_query.first()
                    # set_password function automatically hashing handle kar leta hai
                    user.set_password(new_pwd) 
                    user.save()

                    # 2. Aapki Custom Table (Register_Master) update
                    custom_user = Register_Master.objects.get(Email=email)
                    custom_user.Password = new_pwd
                    custom_user.save()

                    MSG = "Password Updated Successfully! You can now login."
                else:
                    MSG = "Error: This Email is not registered with us."

            except Register_Master.DoesNotExist:
                MSG = "Error: Email found in Auth but not in Custom Table."
            except Exception as e:
                MSG = f"An unexpected error occurred: {e}"

        return render(request, "forget_password.html", {"MSG": MSG})