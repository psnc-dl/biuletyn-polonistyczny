# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils import timezone
from django.utils.html import strip_tags
from reversion.admin import VersionAdmin

from bportal.account.profile.models import UserProfile
from bportal.module.common.utils import remove_unnecessary_tags_from_title, slugify_text_title

from .forms import EducationalOfferTypeAdminForm, EducationalOfferModeAdminForm, EducationalOfferAdminForm, EducationalOfferConfirmAdminForm, EducationalOfferFileForm, EducationalOfferLinkForm, EducationalOfferContentContributionAdminForm
from .models import EducationalOfferFile, EducationalOfferLink, EducationalOfferContentContribution, EducationalOfferAuthorized, EducationalOfferModification


class EducationalOfferModeAdmin(admin.ModelAdmin):
    list_display = ('mode_name',)
    form = EducationalOfferModeAdminForm


class EducationalOfferTypeAdmin(admin.ModelAdmin):
    list_display = ('type_name',)
    form = EducationalOfferTypeAdminForm


class EducationalOfferFileAdminInline(admin.TabularInline):
    model = EducationalOfferFile
    form = EducationalOfferFileForm
    extra = 1


class EducationalOfferLinkAdminInline(admin.TabularInline):
    model = EducationalOfferLink
    form = EducationalOfferLinkForm
    extra = 1


class EducationalOfferContentContributionAdminInline(admin.TabularInline):
    model = EducationalOfferContentContribution
    form = EducationalOfferContentContributionAdminForm
    extra = 1    
    
         
class EducationalOfferAdmin(VersionAdmin):
    list_display = ('eduoffer_position_safe', 'eduoffer_institution', 'eduoffer_date_add', 'eduoffer_added_by', 'eduoffer_date_edit', 'eduoffer_modified_by')
    inlines = (EducationalOfferFileAdminInline, EducationalOfferLinkAdminInline, EducationalOfferContentContributionAdminInline)
    form = EducationalOfferAdminForm
    search_fields = ('eduoffer_position_text',)
    list_filter = ('eduoffer_is_accepted', 'eduoffer_is_promoted')    

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.form = EducationalOfferAdminForm
        else:
            self.form = EducationalOfferConfirmAdminForm
        return super(EducationalOfferAdmin, self).get_form(request, obj, **kwargs)
    
    def save_model(self, request, obj, form, change):
        if obj.eduoffer_added_by is None:
            obj.eduoffer_added_by = request.user
        obj.eduoffer_modified_by = request.user
        obj.eduoffer_position = remove_unnecessary_tags_from_title(obj.eduoffer_position)
        obj.eduoffer_position_text = strip_tags(obj.eduoffer_position)
        obj.eduoffer_position_slug = slugify_text_title(obj.eduoffer_position_text)
        
        super(VersionAdmin, self).save_model(request, obj, form, change)
              
        modification = EducationalOfferModification.objects.create(eduoffer=obj, user=request.user, date_time=timezone.now())
          
        profile = UserProfile.objects.get(user=request.user)
        authorized = EducationalOfferAuthorized.objects.filter(eduoffer=obj);
        if not authorized.exists() :
            institutions = profile.user_institution.all()
            for institution in institutions:
                EducationalOfferAuthorized.objects.create(eduoffer=obj, authorized=institution)    
        profile.user_last_edit_date_time = modification.date_time
        profile.save()       
