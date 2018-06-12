# -*- coding: utf-8 -*-
from django.contrib.admin.options import ModelAdmin

from bportal.account.newsletter.forms import NewsletterCustomContentAdminForm
from bportal.account.newsletter.models import NewsletterCustomContent

from .forms import NewsletterConfigAdminForm
from .models import NewsletterConfig, ManagementEmail
from bportal.module.common.utils import remove_unnecessary_tags_from_title
from django.utils.html import strip_tags


class NewsletterConfigAdmin(ModelAdmin):
    list_display = ('user',)
    model = NewsletterConfig
    form = NewsletterConfigAdminForm
    
class ManagementEmailAdmin(ModelAdmin):
    list_display = ('title',)
    model = ManagementEmail
    
class NewsletterCustomContentAdmin(ModelAdmin):
    list_display = ('title', 'valid_until',)
    model = NewsletterCustomContent
    form = NewsletterCustomContentAdminForm
    
    def save_model(self, request, obj, form, change):
        obj.title = strip_tags(obj.title) 
        obj.title = remove_unnecessary_tags_from_title(obj.title)                 
        super(NewsletterCustomContentAdmin, self).save_model(request, obj, form, change)