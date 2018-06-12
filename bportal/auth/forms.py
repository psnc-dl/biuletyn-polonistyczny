# -*- coding: utf-8 -*-
import re

from captcha.fields import CaptchaField
from dal import autocomplete
from django import forms
from django.contrib import auth 
from django.contrib.auth.forms import AuthenticationForm
from django.template import loader
from phonenumber_field.formfields import PhoneNumberField

from bportal.module.institution.models import Institution

from .fields import FieldRegistration
from .messages import MessageResetPassword
from .tools import send_html_mail


class LoginForm(AuthenticationForm):
    message = forms.CharField(required=False)


class RegistrationForm(forms.Form):
    first_name = forms.CharField(label=FieldRegistration.FIRST_NAME, widget=forms.TextInput(attrs={'class': 'registration__form--input'}))
    last_name = forms.CharField(label=FieldRegistration.LAST_NAME, widget=forms.TextInput(attrs={'class': 'registration__form--input'}))
    username = forms.CharField(label=FieldRegistration.USERNAME, widget=forms.TextInput(attrs={'class': 'registration__form--input'}))
    email = forms.EmailField(label=FieldRegistration.EMAIL, widget=forms.TextInput(attrs={'class': 'registration__form--input'}))
    password = forms.CharField(label=FieldRegistration.PASSWORD, widget=forms.PasswordInput(attrs={'class': 'registration__form--input'}))
    password_repeated = forms.CharField(label=FieldRegistration.PASSWORD_REPEATED, widget=forms.PasswordInput(attrs={'class': 'registration__form--input'}),help_text="Hasło powinno liczyć od 6 do 12 znaków oraz zawierać cyfry i litery.")
    born_date = forms.DateField(label=FieldRegistration.BORN_DATE,required=False, widget=forms.DateInput(attrs={'class': 'registration__form--input datepicker'}), input_formats=['%d.%m.%Y'])
    phone = PhoneNumberField(label=FieldRegistration.PHONE, required=False, widget=forms.TextInput(attrs={'placeholder': 'np. +48777888999', 'class': 'registration__form--input'}))
    captcha = CaptchaField()
    institution = forms.ModelMultipleChoiceField(label=FieldRegistration.INSTITUTION, queryset=Institution.objects.all(), widget=autocomplete.ModelSelect2Multiple(url='institution-autocomplete'))
    rules_accepted = forms.BooleanField(label=FieldRegistration.RULES_ACCEPTED, required=True)


class SetPasswordForm(auth.forms.SetPasswordForm):

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(MessageResetPassword.DIFFERENT_PASSWORDS)
            else:
                regex = re.compile('^(?=.*\d)(?=.*[a-z]).{6,12}$')
                if not regex.match(password1):
                    raise forms.ValidationError(MessageResetPassword.WRONG_PASSWORD)
        return password2


class PasswordResetForm(auth.forms.PasswordResetForm):
    
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        subject = loader.render_to_string(subject_template_name, context)
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)
        send_html_mail(subject, body, from_email, [to_email])
    

