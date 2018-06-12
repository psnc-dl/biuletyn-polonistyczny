# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils import timezone
from django.utils.html import strip_tags
from reversion.admin import VersionAdmin

from bportal.account.profile.models import UserProfile
from bportal.module.common.utils import remove_unnecessary_tags_from_title, slugify_text_title

from .forms import JournalIssueAdminForm, JournalIssueConfirmAdminForm, JournalIssueFileForm, JournalIssueLinkForm, JournalIssueContentContributionAdminForm
from .models import JournalIssueFile, JournalIssueLink, JournalIssueContentContribution, JournalIssueAuthorized, JournalIssueModification
from bportal.module.journal.forms import JournalAdminForm,\
    JournalConfirmAdminForm

class JournalAdmin(VersionAdmin):
    list_display = ('journal_title_safe', 'journal_publisher', 'journal_editor_in_chief',)
    search_fields = ('journal_title_text',)    

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.form = JournalAdminForm
        else:
            self.form = JournalConfirmAdminForm
        return super(JournalAdmin, self).get_form(request, obj, **kwargs)
    
    def save_model(self, request, obj, form, change):
        obj.journal_title = remove_unnecessary_tags_from_title(obj.journal_title)
        obj.journal_title_text = strip_tags(obj.journal_title)          
        obj.journal_title_slug = slugify_text_title(obj.journal_title_text)
                  
        super(VersionAdmin, self).save_model(request, obj, form, change)
        
class JournalIssueFileAdminInline(admin.TabularInline):
    model = JournalIssueFile
    form = JournalIssueFileForm
    extra = 1


class JournalIssueLinkAdminInline(admin.TabularInline):
    model = JournalIssueLink
    form = JournalIssueLinkForm
    extra = 1


class JournalIssueContentContributionAdminInline(admin.TabularInline):
    model = JournalIssueContentContribution
    form = JournalIssueContentContributionAdminForm
    extra = 1    

         
class JournalIssueAdmin(VersionAdmin):
    list_display = ('journalissue_title_safe', 'journalissue_date_add', 'journalissue_added_by', 'journalissue_date_edit', 'journalissue_modified_by',)
    inlines = (JournalIssueFileAdminInline, JournalIssueLinkAdminInline, JournalIssueContentContributionAdminInline)
    form = JournalIssueAdminForm
    search_fields = ('journalissue_title_text',)
    list_filter = ('journalissue_is_accepted', 'journalissue_is_promoted')    

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.form = JournalIssueAdminForm
        else:
            self.form = JournalIssueConfirmAdminForm
        return super(JournalIssueAdmin, self).get_form(request, obj, **kwargs)
    
    def save_model(self, request, obj, form, change):
        if obj.journalissue_added_by is None:
            obj.journalissue_added_by = request.user
        obj.journalissue_modified_by = request.user
        obj.journalissue_title = remove_unnecessary_tags_from_title(obj.journalissue_title)
        obj.journalissue_title_text = strip_tags(obj.journalissue_title)          
        obj.journalissue_title_slug = slugify_text_title(obj.journalissue_title_text)
                  
        super(VersionAdmin, self).save_model(request, obj, form, change)
          
        modification = JournalIssueModification.objects.create(journalissue=obj, user=request.user, date_time=timezone.now())
          
        profile = UserProfile.objects.get(user=request.user)
        authorized = JournalIssueAuthorized.objects.filter(journalissue=obj);
        if not authorized.exists() :
            institutions = profile.user_institution.all()
            for institution in institutions:
                JournalIssueAuthorized.objects.create(journalissue=obj, authorized=institution)
        profile.user_last_edit_date_time = modification.date_time
        profile.save()
