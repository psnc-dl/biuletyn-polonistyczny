# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils import timezone
from django.utils.html import strip_tags
from reversion.admin import VersionAdmin

from bportal.account.profile.models import UserProfile
from bportal.module.common.utils import remove_unnecessary_tags_from_title, slugify_text_title

from .forms import ScholarshipTypeAdminForm, ScholarshipAdminForm, ScholarshipConfirmAdminForm, ScholarshipFileForm, ScholarshipLinkForm, ScholarshipContentContributionAdminForm
from .models import ScholarshipFile, ScholarshipLink, ScholarshipContentContribution, ScholarshipAuthorized, ScholarshipModification


class ScholarshipTypeAdmin(admin.ModelAdmin):
    list_display = ('type_name',)
    form = ScholarshipTypeAdminForm


class ScholarshipFileAdminInline(admin.TabularInline):
    model = ScholarshipFile
    form = ScholarshipFileForm
    extra = 1


class ScholarshipLinkAdminInline(admin.TabularInline):
    model = ScholarshipLink
    form = ScholarshipLinkForm
    extra = 1
    

class ScholarshipContentContributionAdminInline(admin.TabularInline):
    model = ScholarshipContentContribution
    form = ScholarshipContentContributionAdminForm
    extra = 1 
    
         
class ScholarshipAdmin(VersionAdmin):
    list_display = ('scholarship_name_safe', 'scholarship_founder', 'scholarship_date_add', 'scholarship_added_by', 'scholarship_date_edit', 'scholarship_modified_by', )
    inlines = (ScholarshipFileAdminInline, ScholarshipLinkAdminInline, ScholarshipContentContributionAdminInline)    
    form = ScholarshipAdminForm
    search_fields = ('scholarship_name_text', 'scholarship_founder__institution_fullname',)  
    list_filter = ('scholarship_is_accepted', 'scholarship_is_promoted')        

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.form = ScholarshipAdminForm
        else:
            self.form = ScholarshipConfirmAdminForm
        return super(ScholarshipAdmin, self).get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        if obj.scholarship_added_by is None:
            obj.scholarship_added_by = request.user
        obj.scholarship_modified_by = request.user
        obj.scholarship_name = remove_unnecessary_tags_from_title(obj.scholarship_name)
        obj.scholarship_name_text = strip_tags(obj.scholarship_name)
        obj.scholarship_name_slug = slugify_text_title(obj.scholarship_name_text)        

        super(VersionAdmin, self).save_model(request, obj, form, change)

        modification = ScholarshipModification.objects.create(scholarship=obj, user=request.user, date_time=timezone.now())

        profile = UserProfile.objects.get(user=request.user)
        authorized = ScholarshipAuthorized.objects.filter(scholarship=obj);
        if not authorized.exists() :
            institutions = profile.user_institution.all()
            for institution in institutions:
                ScholarshipAuthorized.objects.create(scholarship=obj, authorized=institution)
        profile.user_last_edit_date_time = modification.date_time
        profile.save()
