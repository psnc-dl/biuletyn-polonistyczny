# -*- coding: utf-8 -*-
from uuid import UUID

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render

from bportal.account.profile.forms import PhotoProfileForm
from bportal.newsletter.tools import NewsletterGenerator

from .forms import NewsletterConfigForm
from .models import NEWSPERIOD_NOT
from .models import NewsletterConfig


def newsletter(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            
            newsletter_config = None
            if request.user.userprofile is not None:
                try:
                    newsletter_config  = NewsletterConfig.objects.get(user=request.user.userprofile)
                except NewsletterConfig.DoesNotExist:
                    newsletter_config = NewsletterConfig()
                    newsletter_config.user = request.user.userprofile
                    newsletter_config.save()
                    
                newsletter_form = NewsletterConfigForm(request.POST, instance=newsletter_config)
                photo_form = PhotoProfileForm(request.POST)

            if newsletter_form.is_valid():
                newsletter_config = newsletter_form.save(commit=False)
                newsletter_config.user = request.user.userprofile
                newsletter_config.save()
                newsletter_form.save_m2m()
                
            if photo_form.is_valid():
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
                photo_form = PhotoProfileForm(initial = photo_data)
                      
        else:
            newsletter_config = None
            if request.user.userprofile is not None:
                try:
                    newsletter_config  = NewsletterConfig.objects.get(user=request.user.userprofile)
                except NewsletterConfig.DoesNotExist:
                    newsletter_config = NewsletterConfig()
                    newsletter_config.user = request.user.userprofile
                    newsletter_config.save()
                newsletter_form = NewsletterConfigForm(instance=newsletter_config)
                
                photo_data = {'photo': request.user.userprofile.user_photo, 'remove': False}
                photo_form = PhotoProfileForm(initial=photo_data)
                
        return render(request, 'bportal/account/newsletter.html', { "newsletter_form" : newsletter_form, "photo_form" : photo_form })
    else:
        redirect('home')


def cancel_newsletter(request, uuid=None):
    try:
        userUUID = UUID(request.GET.get('uuid'))
        newsletter_config = NewsletterConfig.objects.get(UUID=userUUID)    
        newsletter_config.period = NEWSPERIOD_NOT
        newsletter_config.UUID = None
        newsletter_config.save() 
        messages.add_message(request, messages.INFO, 'Potwierdzamy rezygnację z otrzymywania newslettera')
        return redirect('home')
    except NewsletterConfig.DoesNotExist:
        raise Http404("token nieaktywny")
    except ValueError:
        raise Http404("błędny token")
    
    
def generate_newsletter(request):
    if request.method == 'GET':
        user = request.user
        generator = NewsletterGenerator()
        return generator.generateNewsHttpResponseForUser(user)
    else:
        redirect('home')
    