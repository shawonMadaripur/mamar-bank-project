from django.shortcuts import render, redirect
from django.views.generic import FormView
from .forms import UserRegistrationForm, UserUpdateForm
from django.contrib.auth import login, logout
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
# Create your views here.

class UserRegistrationView(FormView):
  template_name = 'accounts/user_registration.html'
  form_class = UserRegistrationForm
  success_url = reverse_lazy('register')

  def form_valid(self, form):
    print(form.cleaned_data)
    user = form.save()
    login(self.request, user)
    print(user)
    return super().form_valid(form)
  

class UserLoginView(LoginView):
  template_name = 'accounts/user_login.html'
  def get_success_url(self):
    return reverse_lazy('home')
  
# class UserLogoutView(LogoutView):
#    def get_success_url(self):
#     if self.request.user.is_authenticated:
#       logout(self.request)
#     return reverse_lazy('home')

def UserLogoutView(request):
  logout(request)
  return redirect('home')


# class UserUpdateView(FormView):
#   template_name = 'accounts/user_profile.html'
#   form_class = UserUpdateForm
#   success_url = reverse_lazy('profile')

#   def form_valid(self, form):
#     form.save()
#     return super().form_valid(form)


class UserUpdateView(FormView):
    template_name = 'accounts/user_profile.html'
    form_class = UserUpdateForm
    success_url = reverse_lazy('update')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user  # Pass the logged-in user as the instance
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)



  