from django.shortcuts import render, redirect
from django.contrib.auth import login

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