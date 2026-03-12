from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.http import HttpResponse, HttpResponseBadRequest
from .models import User, PasswordResetToken
from .forms import LoginForm, RegistrationForm, PasswordResetRequestForm, PasswordResetForm
import uuid

def login_view(request):
    """
    Handle user login.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Login successful.")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

@login_required
def logout_view(request):
    """
    Handle user logout.
    """
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')

def register_view(request):
    """
    Handle new user registration.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            messages.success(request, "Registration successful. Please log in.")
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def password_reset_request_view(request):
    """
    Handle password reset request (send token).
    """
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                token = str(uuid.uuid4())
                PasswordResetToken.objects.create(user=user, token=token, created_at=timezone.now())
                # In production, send token via email. Here, display for demo.
                messages.success(request, f"Password reset token: {token}")
                return redirect('password_reset')
            except User.DoesNotExist:
                messages.error(request, "No user found with that email address.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordResetRequestForm()
    return render(request, 'password_reset_request.html', {'form': form})

def password_reset_view(request):
    """
    Handle password reset using token.
    """
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data['token']
            password = form.cleaned_data['password1']
            try:
                reset_token = PasswordResetToken.objects.get(token=token, is_used=False)
                user = reset_token.user
                user.set_password(password)
                user.save()
                reset_token.is_used = True
                reset_token.save()
                messages.success(request, "Password reset successful. Please log in.")
                return redirect('login')
            except PasswordResetToken.DoesNotExist:
                messages.error(request, "Invalid or expired token.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordResetForm()
    return render(request, 'password_reset.html', {'form': form})