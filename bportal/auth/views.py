# -*- coding: utf-8 -*-
import re
import uuid

from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import  Http404
from django.shortcuts import render, redirect

from bportal.account.newsletter.models import NEWSPERIOD_MONTH, NewsletterConfig
from bportal.account.profile.models import UserProfile
from bportal.module.event.models import EventCategory
from bportal.settings import BPORTAL_HOST, BPORTAL_CONTACT_EMAIL_ADDRES_FROM

from .forms import RegistrationForm
from .messages import MessageRegistration
from .tools import send_html_mail


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if not form.errors :
            if form.is_valid :
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                username = form.cleaned_data['username']
                email = form.cleaned_data['email']
                born_date = form.cleaned_data['born_date']
                phone = form.cleaned_data['phone']
                institutions = form.cleaned_data['institution']
                password = form.cleaned_data['password']
                password_repeated = form.cleaned_data['password_repeated']
                regex = re.compile('^(?=.*\d)(?=.*[a-z]).{6,12}$')
                if not regex.match(password):
                    messages.error(request, MessageRegistration.WRONG_PASSWORD);
                else:
                    if password != password_repeated:
                        messages.error(request, MessageRegistration.DIFFERENT_PASSWORDS);
                    else :
                        user_created = False
                        try:
                            user = User.objects.get(Q(username=username) | Q(username=email))   
                        except User.DoesNotExist:                                            
                            user = User.objects.create_user(username, email, password, first_name=first_name, last_name=last_name)
                            user.is_active = False
                            user.save()
                            profile = UserProfile.objects.create(user=user, user_nick=username, user_born_date=born_date, user_phone=phone)
                            profile.user_newsletter_flag = True
                            profile.UUID = str(uuid.uuid4())
                            userNewsConfig = NewsletterConfig.objects.create(user=profile)
                            userNewsConfig.period = NEWSPERIOD_MONTH
                            userNewsConfig.dissertation = True
                            userNewsConfig.project = True
                            userNewsConfig.competition = True
                            userNewsConfig.joboffer = True
                            userNewsConfig.eduoffer = True
                            userNewsConfig.scholarship = True
                            userNewsConfig.event_categories = EventCategory.objects.all()
                            userNewsConfig.save()
                            for institution in institutions:
                                profile.user_institution.add(institution)
                            profile.save()
                            user_created = True
                        try: 
                            user_profile = UserProfile.objects.get(Q(user=user) & Q(user_newsletter_flag=False))
                            messages.error(request, MessageRegistration.LOGIN_EXISTS);
                        except UserProfile.DoesNotExist:
                            user.is_active = False
                            user.username = username
                            user.set_password(password)
                            user.email = email
                            user.first_name = first_name
                            user.last_name = last_name
                            user.save()
                            user_profile = UserProfile.objects.get(user=user)
                            user_profile.user_newsletter_flag = False
                            user_profile.save()
                            user_created = True
                            
                        if user_created:
                            form = RegistrationForm()
                            title = 'Biuletyn Polonistyczny - planowane funkcjonalności'
                            message = 'Szanowni Państwo,\n'
                            message += 'Pragnąc sprostać oczekiwaniom Użytkowników "Biuletynu Polonistycznego" zwracamy się do Państwa z prośbą o wyrażenie opinii na temat obecnych i planowanych funkcjonalności "Biuletynu".\n'
                            message += 'Dziękujemy za poświęcenie kilku minut na odpowiedź na poniższe pytania.\n'
                            message += 'Zespół "Biuletynu Polonistycznego"\n\n'
                            message += first_name
                            message += ', zapraszamy Cię do wypełnienia formularza Biuletyn Polonistyczny - planowane funkcjonalności. Aby go wypełnić, odwiedź stronę:\n'
                            message += 'https://docs.google.com/forms/d/1SUkPEqHftZ1HrUTC41E3y_h-JRtBX6l9uATplvV_nBc/viewform'
                            message += '\n\nAby aktywować konto kliknij link: ' + BPORTAL_HOST + '/' + 'registration/activate?uuid=' + str(profile.UUID)
                            send_html_mail(title, message, 'Redakcja Biuletynu Polonistycznego ' + '<' + BPORTAL_CONTACT_EMAIL_ADDRES_FROM + '>', [email])
                            messages.success(request, MessageRegistration.ACCOUNT_CREATED)
    else:
        form = RegistrationForm()
 
    return render(request, 'bportal/auth/registration.html', { "form" : form })

def activate(request):
    try:
        userUUID = request.GET.get('uuid')
        user_profile = UserProfile.objects.get(UUID=userUUID)
        user = user_profile.user
        user.is_active = True
        user_profile.UUID = None
        user.save()
        user_profile.save()
        messages.add_message(request, messages.INFO, 'Twoje konto zostało aktywowane. Możesz się teraz zalogować.')
        return redirect('home')
    except UserProfile.DoesNotExist:
        raise Http404("token niekatywny")
    except ValueError:
        raise Http404("błędny token")
    
