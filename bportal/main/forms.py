# -*- coding: utf-8 -*-
from .fields import FieldContactMessage
from .fields import FieldNewsletterSubscription
from django import forms
from phonenumber_field.formfields import PhoneNumberField
from captcha.fields import CaptchaField

class ContactMessageForm(forms.Form):
    firstname = forms.CharField(label=FieldContactMessage.FIRSTNAME, widget=forms.TextInput(attrs={'class': 'contact__form--input'}))
    email = forms.EmailField(label=FieldContactMessage.EMAIL, widget=forms.TextInput(attrs={'class': 'contact__form--input'}))
    phone = PhoneNumberField(label=FieldContactMessage.PHONE, required=False, widget=forms.TextInput(attrs={'class': 'contact__form--input'}))
    title = forms.CharField(label=FieldContactMessage.TITLE, widget=forms.TextInput(attrs={'class': 'contact__form--input'}))
    message = forms.CharField(label=FieldContactMessage.MESSAGE, widget=forms.Textarea(attrs={'class': 'contact__form--textarea'}))
    captcha = CaptchaField()
    
class NewsletterSubscriptionForm(forms.Form):
    news_email = forms.EmailField(label=FieldNewsletterSubscription.EMAIL, widget=forms.TextInput(attrs={'class': 'contact__form--input'}))
    captcha = CaptchaField(id_prefix = 'news')
