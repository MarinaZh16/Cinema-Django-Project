from django import forms
from . import models
from django.forms import ModelForm



class UserForm(ModelForm):
    password = forms.CharField(required=True, widget=forms.PasswordInput)
    password2 = forms.CharField(required=True, widget=forms.PasswordInput)

    class Meta:
        model = models.User
        fields = ['username', 'email']

    def clean_password(self):
        if self.data['password'] != self.data['password2']:
            raise forms.ValidationError('Password don\'t match.')
        return self.data['password']


