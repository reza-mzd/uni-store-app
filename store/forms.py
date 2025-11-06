from django import forms
from django.core import validators

class MyForm(forms.Form):
    username = forms.ChoiceField(validators=[validators.RegexValidator(r'(?! +)')])
    password = forms.CharField(widget=forms.PasswordInput())
    email = forms.EmailField()
    age = forms.IntegerField(min_value=1)