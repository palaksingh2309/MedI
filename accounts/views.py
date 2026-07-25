from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View

from .forms import CustomUserCreationForm, UserProfileForm

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Account created successfully! Please login.")
        return response

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    
    def form_valid(self, form):
        messages.success(self.request, f"Welcome back, {form.get_user().username}!")
        return super().form_valid(form)

class CustomLogoutView(LogoutView):
    next_page = 'accounts:login'
    
    def dispatch(self, request, *args, **kwargs):
        messages.info(request, "You have been logged out.")
        return super().dispatch(request, *args, **kwargs)

from .forms import CustomUserCreationForm, UserProfileForm, HealthProfileForm
from dashboard.models import HealthProfile

class ProfileView(LoginRequiredMixin, View):
    template_name = 'accounts/profile.html'

    def get(self, request):
        profile, _ = HealthProfile.objects.get_or_create(user=request.user)
        user_form = UserProfileForm(instance=request.user)
        health_form = HealthProfileForm(instance=profile)
        
        active_tab = request.GET.get('tab', 'personal')
        
        return render(request, self.template_name, {
            'user_form': user_form,
            'health_form': health_form,
            'active_tab': active_tab,
            'profile': profile
        })

    def post(self, request):
        profile, _ = HealthProfile.objects.get_or_create(user=request.user)
        user_form = UserProfileForm(instance=request.user)
        health_form = HealthProfileForm(instance=profile)
        
        form_type = request.POST.get('form_type')
        active_tab = 'personal'
        
        if form_type == 'personal':
            user_form = UserProfileForm(request.POST, request.FILES, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, "Account settings updated successfully!")
                return redirect('/accounts/profile/?tab=personal')
            else:
                messages.error(request, "Error updating account settings.")
                active_tab = 'personal'
        elif form_type == 'health':
            health_form = HealthProfileForm(request.POST, instance=profile)
            if health_form.is_valid():
                health_form.save()
                messages.success(request, "Clinical Health Profile updated successfully!")
                return redirect('/accounts/profile/?tab=health')
            else:
                messages.error(request, "Error updating Health Profile metrics.")
                active_tab = 'health'
                
        return render(request, self.template_name, {
            'user_form': user_form,
            'health_form': health_form,
            'active_tab': active_tab,
            'profile': profile
        })
