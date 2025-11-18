from django.shortcuts import render
from django.contrib.auth.views import LoginView as DJ_LoginView
from . import forms

class LoginView(DJ_LoginView):
        redirect_authenticated_user = True
        form_class = forms.LoginForm