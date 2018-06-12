# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils import timezone
from django.utils.html import strip_tags
from reversion.admin import VersionAdmin

from bportal.account.profile.models import UserProfile
from bportal.module.common.utils import remove_unnecessary_tags_from_title, slugify_text_title

from .forms import CompetitionAdminForm, CompetitionConfirmAdminForm, CompetitionFileForm, CompetitionLinkForm, CompetitionContentContributionAdminForm
from .models import CompetitionFile, CompetitionLink, CompetitionContentContribution, CompetitionAuthorized, CompetitionModification


class CompetitionFileAdminInline(admin.TabularInline):
    model = CompetitionFile
    form = CompetitionFileForm
    extra = 1


class CompetitionLinkAdminInline(admin.TabularInline):
    model = CompetitionLink
    form = CompetitionLinkForm
    extra = 1
    

class CompetitionContentContributionAdminInline(admin.TabularInline):
    model = CompetitionContentContribution
    form = CompetitionContentContributionAdminForm
    extra = 1  
    

class CompetitionAdmin(VersionAdmin):
    list_display = ('competition_title_safe', 'competition_date_add', 'competition_added_by', 'competition_date_edit', 'competition_modified_by')
    inlines = (CompetitionFileAdminInline, CompetitionLinkAdminInline, CompetitionContentContributionAdminInline)
    form = CompetitionAdminForm
    search_fields = ('competition_title_text',)
    list_filter = ('competition_is_accepted', 'competition_is_promoted')
    
    
    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.form = CompetitionAdminForm
        else:
            self.form = CompetitionConfirmAdminForm
        return super(CompetitionAdmin, self).get_form(request, obj, **kwargs)
    
    def save_model(self, request, obj, form, change):
        if obj.competition_added_by is None:
            obj.competition_added_by = request.user
        obj.competition_modified_by = request.user
        obj.competition_title = remove_unnecessary_tags_from_title(obj.competition_title)
        obj.competition_title_text = strip_tags(obj.competition_title)
        obj.competition_title_slug = slugify_text_title(obj.competition_title_text)        
                          
        super(VersionAdmin, self).save_model(request, obj, form, change)
          
        modification = CompetitionModification.objects.create(competition=obj, user=request.user, date_time=timezone.now())
          
        profile = UserProfile.objects.get(user=request.user)
        authorized = CompetitionAuthorized.objects.filter(competition=obj);
        if not authorized.exists() :
            institutions = profile.user_institution.all()
            for institution in institutions:
                CompetitionAuthorized.objects.create(competition=obj, authorized=institution)
        profile.user_last_edit_date_time = modification.date_time
        profile.save()
