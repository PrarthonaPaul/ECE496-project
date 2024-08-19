from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login


#Creating a view for the registration process
def register(request):
    #if block is for users who are already registered. This checks password and redirects to user-landing page
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect('user_landing')
    #else block is for first time registration
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})