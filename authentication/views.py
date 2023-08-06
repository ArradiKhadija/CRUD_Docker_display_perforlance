from django import forms
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib.auth import login,logout,authenticate


def signupView(request):
    error_message = None

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        else:
            error_message = "Password is too similar to the username or contains invalid characters."
    else:
        form = UserCreationForm()

    return render(request, 'signup.html', {'form': form, 'error_message': error_message})
    


def loginView(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('gerer_docker')
            else:
                error_message = 'Invalid username or password'
        else:
            error_message = 'Invalid username or password'
    else:
        form = AuthenticationForm()
        error_message = None
        
    return render(request, 'login.html', {'form': form, 'error_message': error_message})







def logoutView(request):
    logout(request)
    return redirect('login')

