# -*- coding: utf-8 -*-
import re

from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import PersonalDataProfileForm, PasswordProfileForm, PhotoProfileForm
from .messages import MessageProfile
from .models import UserProfile


def user_profile(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            if 'edit_password' in request.POST:
                profile_data = {'first_name': request.user.first_name, 'last_name': request.user.last_name,
                            'nick': request.user.userprofile.user_nick, 'email': request.user.email,
                            'born_date': request.user.userprofile.user_born_date, 'phone': request.user.userprofile.user_phone, }
                profile_form = PersonalDataProfileForm(initial=profile_data)
                photo_data = {'photo': request.user.userprofile.user_photo, 'remove': False}
                photo_form = PhotoProfileForm(initial=photo_data)
                password_form = PasswordProfileForm(request.POST)
                if not password_form.errors :
                    if password_form.is_valid :
                        password = password_form.cleaned_data['password']
                        password_repeated = password_form.cleaned_data['password_repeated']
                        regex = re.compile('^(?=.*\d)(?=.*[a-z]).{6,12}$')
                        if not regex.match(password):
                            password_form.add_error('password', MessageProfile.WRONG_PASSWORD)
                        else:
                            if password != password_repeated:
                                password_form.add_error('password_repeated', MessageProfile.DIFFERENT_PASSWORDS)
                            else:
                                request.user.set_password(password_repeated)
                                request.user.save()
                                messages.success(request, MessageProfile.PASSWORD_EDITED);
                                
            if 'edit_profile' in request.POST:         
                password_data = {'username': request.user.username, }
                password_form = PasswordProfileForm(initial=password_data)
                photo_form = PhotoProfileForm(request.POST)
                profile_form = PersonalDataProfileForm(request.POST)
                
                if not profile_form.errors:
                    if profile_form.is_valid:
                        request.user.first_name = profile_form.cleaned_data['first_name']
                        request.user.last_name = profile_form.cleaned_data['last_name']
                        request.user.userprofile.user_nick = profile_form.cleaned_data['nick']
                        request.user.email = profile_form.cleaned_data['email']
                        request.user.userprofile.user_born_date = profile_form.cleaned_data['born_date']
                        request.user.userprofile.user_phone = profile_form.cleaned_data['phone']
                        request.user.save()
                        request.user.userprofile.save()
                                   
                if not photo_form.errors:
                    if photo_form.is_valid:
                        photo_file = request.FILES.get('photo')
                        photo_remove = photo_form.cleaned_data['remove']
                        if not photo_file is None:
                            request.user.userprofile.user_photo = photo_file
                            request.user.userprofile.save()
                        else:
                            if photo_remove:
                                request.user.userprofile.user_photo.delete() 
                                request.user.userprofile.user_photo = None  
                        photo_data = {'photo': request.user.userprofile.user_photo, 'remove': False}
                        photo_form = PhotoProfileForm(initial=photo_data)      
                 
                messages.success(request, MessageProfile.PROFILE_EDITED)

        else:
            try:
                request.user.userprofile
            except UserProfile.DoesNotExist:
                request.user.userprofile = UserProfile.objects.create(user=request.user)
                
            profile_data = {'first_name': request.user.first_name, 'last_name': request.user.last_name,
                            'nick': request.user.userprofile.user_nick, 'email': request.user.email,
                            'born_date': request.user.userprofile.user_born_date, 'phone': request.user.userprofile.user_phone, }
            profile_form = PersonalDataProfileForm(initial=profile_data)
            
            password_data = {'username': request.user.username, }
            password_form = PasswordProfileForm(initial=password_data)
            
            photo_data = {'photo': request.user.userprofile.user_photo, 'remove': False}
            photo_form = PhotoProfileForm(initial=photo_data)

        return render(request, 'bportal/account/userprofile.html', { "profile_form" : profile_form, "password_form" : password_form, "photo_form" : photo_form })

    else:
        return redirect('home')
