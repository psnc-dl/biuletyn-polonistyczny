# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils import timezone
from django.utils.html import strip_tags
from reversion.admin import VersionAdmin

from bportal.account.profile.models import UserProfile
from bportal.module.common.utils import remove_unnecessary_tags_from_title, slugify_text_title

from .forms import EventCategoryAdminForm, EventFileForm, EventLinkForm, EventContentContributionAdminForm, EventAdminForm, EventConfirmAdminForm, EventSummaryLinkForm, EventSummaryFileForm, EventSummaryPictureForm, EventSummaryPublicationForm, EventSummaryAdminForm, EventSummaryContentContributionAdminForm
from .models import EventFile, EventLink, EventContentContribution, EventSummaryLink, EventSummaryFile, EventSummaryPicture, EventSummaryPublication, EventSummaryContentContribution, EventAuthorized, EventModification


class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ('event_category_name',)
    form = EventCategoryAdminForm


class EventFileAdminInline(admin.TabularInline):
    extra = 1
    form = EventFileForm
    model = EventFile


class EventLinkAdminInline(admin.TabularInline):
    model = EventLink
    form = EventLinkForm
    extra = 1
    

class EventContentContributionAdminInline(admin.TabularInline):
    model = EventContentContribution
    form = EventContentContributionAdminForm
    extra = 1    


class EventAdmin(VersionAdmin):
    list_display = ('event_name_safe', 'event_date_from', 'event_contributors_date', 'event_participants_date', 'event_date_add', 'event_added_by', 'event_date_edit', 'event_modified_by',)
    inlines = (EventFileAdminInline, EventLinkAdminInline, EventContentContributionAdminInline)
    form = EventAdminForm
    search_fields = ('event_name_text',)
    list_filter = ('event_is_accepted', 'event_is_promoted')    
    
    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.form = EventAdminForm
        else:
            self.form = EventConfirmAdminForm
        return super(EventAdmin, self).get_form(request, obj, **kwargs)
   
    def save_model(self, request, obj, form, change):
        if obj.event_added_by is None:
            obj.event_added_by = request.user
        obj.event_modified_by = request.user
        obj.event_name = remove_unnecessary_tags_from_title(obj.event_name)
        obj.event_name_text = strip_tags(obj.event_name)
        obj.event_name_slug = slugify_text_title(obj.event_name_text)           
                  
        super(VersionAdmin, self).save_model(request, obj, form, change)
          
        modification = EventModification.objects.create(event=obj, user=request.user, date_time=timezone.now())
          
        profile = UserProfile.objects.get(user=request.user)
        authorized = EventAuthorized.objects.filter(event=obj);
        if not authorized.exists() :
            institutions = profile.user_institution.all()
            for institution in institutions:
                EventAuthorized.objects.create(event=obj, authorized=institution)
        profile.user_last_edit_date_time = modification.date_time
        profile.save() 


class EventSummaryLinkAdminInline(admin.TabularInline):
    model = EventSummaryLink
    form = EventSummaryLinkForm
    extra = 1


class EventSummaryFileAdminInline(admin.TabularInline):
    model = EventSummaryFile
    form = EventSummaryFileForm
    extra = 1


class EventSummaryPictureAdminInline(admin.TabularInline):
    model = EventSummaryPicture
    form = EventSummaryPictureForm    
    extra = 1


class EventSummaryPublicationAdminInline(admin.TabularInline):
    model = EventSummaryPublication
    form = EventSummaryPublicationForm
    extra = 1


class EventSummaryContentContributionAdminInline(admin.TabularInline):
    model = EventSummaryContentContribution
    form = EventSummaryContentContributionAdminForm
    extra = 1    


class EventSummaryAdmin(admin.ModelAdmin):
    list_display = ('get_event_name_safe',)
    inlines = (EventSummaryLinkAdminInline, EventSummaryFileAdminInline, EventSummaryPictureAdminInline, EventSummaryPublicationAdminInline, EventSummaryContentContributionAdminInline)
    form = EventSummaryAdminForm

    def get_event_name_safe(self, obj):
        return obj.event_summary_event.event_name_safe()
