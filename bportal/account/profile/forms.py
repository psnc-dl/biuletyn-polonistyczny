# -*- coding: utf-8 -*-
from dal import autocomplete
from django import forms
from phonenumber_field.formfields import PhoneNumberField

from .fields import FieldPersonalDataProfile, FieldPasswordProfile, FieldPhotoProfile
from .models import UserProfile
from .widgets import UserPhotoWidget


class ProfileAdminForm(forms.ModelForm):
    
    class Meta:
        model = UserProfile
        fields = ('__all__')
        widgets = {
            'user_institution': autocomplete.ModelSelect2Multiple(url='institution-autocomplete'),
            'user_person': autocomplete.ModelSelect2(url='person-autocomplete'),
        }


class PersonalDataProfileForm(forms.Form):
    first_name = forms.CharField(label=FieldPersonalDataProfile.FIRST_NAME, widget=forms.TextInput(attrs={'class': 'account__form--input'}))
    last_name = forms.CharField(label=FieldPersonalDataProfile.LAST_NAME, widget=forms.TextInput(attrs={'class': 'account__form--input'}))
    nick = forms.CharField(label=FieldPersonalDataProfile.NICK, widget=forms.TextInput(attrs={'class': 'account__form--input'}))
    email = forms.EmailField(label=FieldPersonalDataProfile.EMAIL, widget=forms.TextInput(attrs={'class': 'account__form--input'}))
    born_date = forms.DateField(label=FieldPersonalDataProfile.BORN_DATE, required=False, widget=forms.DateInput(attrs={'class': 'account__form--input datepicker'}), input_formats=['%d.%m.%Y'])
    phone = PhoneNumberField(label=FieldPersonalDataProfile.PHONE, required=False, widget=forms.TextInput(attrs={'class': 'account__form--input'}))
    
class PasswordProfileForm(forms.Form):
    username = forms.CharField(label=FieldPasswordProfile.USERNAME, required=False, widget=forms.TextInput(attrs={'class': 'account__form--input'}))
    password = forms.CharField(label=FieldPasswordProfile.PASSWORD, widget=forms.PasswordInput(attrs={'class': 'account__form--input'}))
    password_repeated = forms.CharField(label=FieldPasswordProfile.PASSWORD_REPEATED, widget=forms.PasswordInput(attrs={'class': 'account__form--input'}))
    
class PhotoProfileForm(forms.Form):
    photo = forms.FileField(label=FieldPhotoProfile.NEW_PHOTO, widget=UserPhotoWidget(), required=False)
    remove = forms.BooleanField(label=FieldPhotoProfile.REMOVE_PHOTO, required=False)
