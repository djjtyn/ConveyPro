from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import auth, messages
from django.urls import reverse
from .forms import LoginForm, RegistrationForm
from .models import CustomUser, UserType
from django.utils.safestring import mark_safe

def register(request):
    try:
        form = RegistrationForm()
        # GET REQUEST
        if request.method == "GET":
            # Display Registration Page
            return render(request, 'register.html', {'form': form})
        # POST REQUEST
        if request.method == "POST":
            email = request.POST['email']
            
            # If user already exists
            if CustomUser.objects.filter(email=email).exists():
                # Redirect to the login page
                error_msg = 'Error Registering Account. Already Registered? <a href = "/auth/login/">Login/Reset Password</a>'
                messages.error(request, mark_safe(error_msg))
                return render(request, 'register.html', {'form': form})
            
            # User Creation - will intialise as unverified
            password = request.POST['password']
            #Compay being stored as a string until verified to avoid over population of Company table
            associated_company = request.POST['associated_company']
            # Retrieve selected user type obj
            user_type = UserType.objects.get(pk = request.POST['user_type'])
            user = CustomUser(email=email, user_type = user_type, is_verified = False, non_verified_company = associated_company )
            user.set_password(password)
            user.save()
            # Log the user in 
            auth.login(request, user)
            messages.success(request, "Registration successful!You are now logged in as an unverified account. Additional functionality will become available after a staff member verifies your account.")
            return redirect(reverse('property:view_opportunities'))
    except Exception as e:
        print(f'Error at register(): {e}')


def login(request):
    try:
        #Return If the user is already logged in
        if request.user.is_authenticated:
            messages.info(request, "You are currently logged in")
            return
        form = LoginForm()
        if request.method == "POST":
            user = auth.authenticate(email=request.POST['email'], password=request.POST['password'])
            # If no user is found with matching credentials redirect to login form 
            if user == None:        
                messages.info(request, "Unable to find user matching credentials entered")
                return render(request, 'login.html', {'form': form})
            auth.login(user=user, request=request)
            messages.info(request, "You are now logged in!")
                # If the login page was displayed by user trying to access particular page, redirect user to the page they were trying to access
            if 'next' in request.GET:
                return redirect(request.GET['next'])
            return redirect(reverse('property:view_opportunities'))
        # Display Login Page
        return render(request, 'login.html', {'form': form})
    except Exception as e:
        print(f'Error at login(): {e}')
    
@login_required
def logout(request):
    auth.logout(request)
    messages.info(request, "Logout Successful")
    return redirect(reverse('property:view_opportunities'))