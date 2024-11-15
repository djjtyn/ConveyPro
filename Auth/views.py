from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import auth, messages
from django.urls import reverse
from .forms import LoginForm

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