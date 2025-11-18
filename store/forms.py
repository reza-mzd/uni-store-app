from django import forms
from django.core import validators
from . import models
class MyForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())
    email = forms.EmailField()
    age = forms.IntegerField(min_value=1)

    def clean_username(self):
        if ' '  in self.cleaned_data["username"]:
            raise forms.ValidationError("Username Must not contain spaces")

        return self.cleaned_data.get('username').lower()
    
    def clean(self):
        cleaned_data = super().clean()
        u = cleaned_data.get('username')
        p = cleaned_data.get('password')

        if u == p:
            raise forms.ValidationError('User and Pass must not be same')
        
class CommentForm(forms.ModelForm):
    class Meta:
        model = models.Comment
        fields = ['body']
