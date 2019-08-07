from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm

from .forms import SignUpForm

# Create your views here.
def signup(request):
    if request.method == 'POST':
        userData = (request.POST).copy()
        userData['username'] = userData['username'].lower()
        form = SignUpForm(userData)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

def log_in(request):
    if request.method == 'POST':
        userData = (request.POST).copy()
        userData['username'] = userData['username'].lower()
        form = AuthenticationForm(data=userData)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})