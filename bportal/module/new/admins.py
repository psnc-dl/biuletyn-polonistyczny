# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils import timezone
from django.utils.html import strip_tags
from reversion.admin import VersionAdmin

from bportal.account.profile.models import UserProfile
from bportal.module.common.utils import remove_unnecessary_tags_from_title, slugify_text_title

from .forms import NewCategoryAdminForm, NewAdminForm, NewConfirmAdminForm, NewFileForm, NewLinkForm, NewContentContributionAdminForm
from .models import NewFile, NewLink, NewContentContribution, NewAuthorized, NewModification


class NewCategoryAdmin(admin.ModelAdmin):
    list_display = ('new_category_name',)
    form = NewCategoryAdminForm


class NewFileAdminInline(admin.TabularInline):
    model = NewFile
    form = NewFileForm
    extra = 1


class NewLinkAdminInline(admin.TabularInline):
    model = NewLink
    form = NewLinkForm
    extra = 1


class NewContentContributionAdminInline(admin.TabularInline):
    model = NewContentContribution
    form = NewContentContributionAdminForm
    extra = 1    

         
class NewAdmin(VersionAdmin):
    list_display = ('new_title_safe', 'new_date_add', 'new_added_by', 'new_date_edit', 'new_modified_by',)
    inlines = (NewFileAdminInline, NewLinkAdminInline, NewContentContributionAdminInline)
    form = NewAdminForm
    search_fields = ('new_title_text',)
    list_filter = ('new_is_accepted', 'new_is_promoted')    

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.form = NewAdminForm
        else:
            self.form = NewConfirmAdminForm
        return super(NewAdmin, self).get_form(request, obj, **kwargs)
    
    def save_model(self, request, obj, form, change):
        if obj.new_added_by is None:
            obj.new_added_by = request.user
        obj.new_modified_by = request.user
        obj.new_title = remove_unnecessary_tags_from_title(obj.new_title)
        obj.new_title_text = strip_tags(obj.new_title)          
        obj.new_title_slug = slugify_text_title(obj.new_title_text)
                  
        super(VersionAdmin, self).save_model(request, obj, form, change)
          
        modification = NewModification.objects.create(new=obj, user=request.user, date_time=timezone.now())
          
        profile = UserProfile.objects.get(user=request.user)
        authorized = NewAuthorized.objects.filter(new=obj);
        if not authorized.exists() :
            institutions = profile.user_institution.all()
            for institution in institutions:
                NewAuthorized.objects.create(new=obj, authorized=institution)
        profile.user_last_edit_date_time = modification.date_time
        profile.save()
