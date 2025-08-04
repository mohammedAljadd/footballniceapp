from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from .forms import SignUpForm
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout as django_logout
from django.http import HttpResponseRedirect
from django.urls import reverse

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('match_list')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'  # your own login template
    success_url = '/'  # redirect to home page after login
    
    def get_success_url(self):
        return self.success_url

def custom_logout_view(request):
    """Custom logout view to ensure proper session clearing"""
    django_logout(request)
    # Clear any remaining session data
    request.session.flush()
    return HttpResponseRedirect(reverse('match_list'))