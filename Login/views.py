from django.shortcuts import render, redirect
from Register.models import Register_Master

def login(request):
    msg = ""

    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()

        # Use case-insensitive lookup to avoid minor mismatch
        user = Register_Master.objects.filter(Name__iexact=name, Email__iexact=email).first()

        if user:
            # Save user info in session
            request.session['Name'] = user.Name
            request.session['Email'] = user.Email

            # Redirect to prediction page
            return redirect('predict')
        else:
            msg = "Invalid Name or Email! Please try again."

    return render(request, "login.html", {'msg': msg})
