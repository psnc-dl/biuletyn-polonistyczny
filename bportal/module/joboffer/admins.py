# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils import timezone
from django.utils.html import strip_tags
from reversion.admin import VersionAdmin

from bportal.account.profile.models import UserProfile
from bportal.module.common.utils import remove_unnecessary_tags_from_title, slugify_text_title

from .forms import JobOfferTypeAdminForm, JobOfferDisciplineAdminForm, JobOfferAdminForm, JobOfferConfirmAdminForm, JobOfferFileForm, JobOfferLinkForm, JobOfferContentContributionAdminForm
from .models import JobOfferFile, JobOfferLink, JobOfferContentContribution, JobOfferAuthorized, JobOfferModification


class JobOfferDisciplineAdmin(VersionAdmin):
    list_display = ('discipline_name', )
    form = JobOfferDisciplineAdminForm


class JobOfferTypeAdmin(admin.ModelAdmin):
    list_display = ('type_name',)
    form = JobOfferTypeAdminForm
    

class JobOfferFileAdminInline(admin.TabularInline):
    model = JobOfferFile
    form = JobOfferFileForm
    extra = 1
    
    
class JobOfferLinkAdminInline(admin.TabularInline):
    model = JobOfferLink
    form = JobOfferLinkForm
    extra = 1


class JobOfferContentContributionAdminInline(admin.TabularInline):
    model = JobOfferContentContribution
    form = JobOfferContentContributionAdminForm
    extra = 1            


class JobOfferAdmin(VersionAdmin):
    list_display = ('joboffer_position_safe', 'joboffer_institution', 'joboffer_date_add','joboffer_added_by','joboffer_date_edit','joboffer_modified_by', )
    inlines = (JobOfferFileAdminInline, JobOfferLinkAdminInline, JobOfferContentContributionAdminInline)
    form = JobOfferAdminForm
    search_fields = ('joboffer_position_text',)
    list_filter = ('joboffer_is_accepted', 'joboffer_is_promoted')     
             
    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.form = JobOfferAdminForm
        else:
            self.form = JobOfferConfirmAdminForm
        return super(JobOfferAdmin, self).get_form(request, obj, **kwargs)
                 
    def save_model(self, request, obj, form, change):
        if obj.joboffer_added_by is None:
            obj.joboffer_added_by = request.user
        obj.joboffer_modified_by = request.user
        obj.joboffer_position = remove_unnecessary_tags_from_title(obj.joboffer_position)
        obj.joboffer_position_text = strip_tags(obj.joboffer_position)
        obj.joboffer_position_slug = slugify_text_title(obj.joboffer_position_text)        
        
        super(VersionAdmin, self).save_model(request, obj, form, change)
              
        modification = JobOfferModification.objects.create(joboffer=obj, user=request.user, date_time=timezone.now())
          
        profile = UserProfile.objects.get(user=request.user)
        authorized = JobOfferAuthorized.objects.filter(joboffer=obj);
        if not authorized.exists() :
            institutions = profile.user_institution.all()
            for institution in institutions:
                JobOfferAuthorized.objects.create(joboffer=obj, authorized=institution)
        profile.user_last_edit_date_time = modification.date_time
        profile.save() 
