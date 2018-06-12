# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils import timezone
from django.utils.html import strip_tags
from import_export.admin import ImportExportModelAdmin
from reversion.admin import VersionAdmin

from bportal.account.profile.models import UserProfile
from bportal.module.common.storage import UtfImportExportStorage
from bportal.module.common.utils import remove_unnecessary_tags_from_title, slugify_text_title
from bportal.module.dissertation.resources import DissertationResource
from bportal.settings import DEFAULT_IMPORT_FORMATS

from .forms import DissertationAdminForm, DissertationConfirmAdminForm, DissertationFileForm, DissertationLinkForm, DissertationContentContributionAdminForm
from .models import DissertationFile, DissertationLink, DissertationContentContribution, DissertationAuthorized, DissertationModification

      
class DissertationFileAdminInline(admin.TabularInline):
    model = DissertationFile
    form = DissertationFileForm
    extra = 1


class DissertationLinkAdminInline(admin.TabularInline):
    model = DissertationLink
    form = DissertationLinkForm
    extra = 1


class DissertationContentContributionAdminInline(admin.TabularInline):
    model = DissertationContentContribution
    form = DissertationContentContributionAdminForm
    extra = 1    
    

class DissertationAdmin(ImportExportModelAdmin, VersionAdmin):
    list_display = ('dissertation_title_safe', 'dissertation_date_add', 'dissertation_added_by', 'dissertation_date_edit', 'dissertation_modified_by',)
    inlines = (DissertationFileAdminInline, DissertationLinkAdminInline, DissertationContentContributionAdminInline)
    form = DissertationAdminForm
    resource_class = DissertationResource
    search_fields = ('dissertation_title_text',)
    list_filter = ('dissertation_is_accepted', 'dissertation_is_promoted')
    
    #: template for change_list view
    change_list_template = 'admin/import_export/change_list_import_export_dissertations.html'
    tmp_storage_class = UtfImportExportStorage    
    from_encoding = 'utf-8'
    to_encoding = 'utf-8'
    
    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.form = DissertationAdminForm
        else:
            self.form = DissertationConfirmAdminForm
        return super(DissertationAdmin, self).get_form(request, obj, **kwargs)
    
    def get_import_formats(self):
        return [f for f in self.formats if f().can_import() and f().get_title() in DEFAULT_IMPORT_FORMATS]
   
    def save_model(self, request, obj, form, change):
        if obj.dissertation_added_by is None:
            obj.dissertation_added_by = request.user
        obj.dissertation_modified_by = request.user
        obj.dissertation_title = remove_unnecessary_tags_from_title(obj.dissertation_title)
        obj.dissertation_title_text = strip_tags(obj.dissertation_title)
        obj.dissertation_title_slug = slugify_text_title(obj.dissertation_title_text)
                  
        super(VersionAdmin, self).save_model(request, obj, form, change)
          
        modification = DissertationModification.objects.create(dissertation=obj, user=request.user, date_time=timezone.now())
          
        profile = UserProfile.objects.get(user=request.user)
        authorized = DissertationAuthorized.objects.filter(dissertation=obj);
        if not authorized.exists() :
            institutions = profile.user_institution.all()
            for institution in institutions:
                DissertationAuthorized.objects.create(dissertation=obj, authorized=institution)
        profile.user_last_edit_date_time = modification.date_time
        profile.save()
