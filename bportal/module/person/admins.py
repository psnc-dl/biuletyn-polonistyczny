# -*- coding: utf-8 -*-

from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from reversion.admin import VersionAdmin

from bportal.module.common.storage import UtfImportExportStorage
from bportal.module.common.utils import slugify_text_title
from bportal.module.person.forms import PersonAdminForm, PersonConfirmAdminForm, PersonAffiliationForm
from bportal.module.person.models import PersonAffiliation
from bportal.module.person.resources import PersonResource
from bportal.settings import DEFAULT_IMPORT_FORMATS


class PersonAffiliationAdminInline(admin.TabularInline):
    model = PersonAffiliation
    form = PersonAffiliationForm
    extra = 1
          
          
class PersonAdmin(ImportExportModelAdmin, VersionAdmin):
    list_display = ('person_first_name', 'person_last_name')
    form = PersonAdminForm
    inlines = (PersonAffiliationAdminInline,)
    resource_class = PersonResource
    search_fields = ('person_first_name', 'person_last_name',)
    
    # : template for change_list view
    change_list_template = 'admin/import_export/change_list_import_export_people.html'
    tmp_storage_class = UtfImportExportStorage    
    from_encoding = 'utf-8'
    to_encoding = 'utf-8'
        
    def get_form(self, request, obj=None, **kwargs):
        
        if obj:
            self.form = PersonAdminForm
        else:
            self.form = PersonConfirmAdminForm
        return super(PersonAdmin, self).get_form(request, obj, **kwargs)
    
    def get_import_formats(self):
        return [f for f in self.formats if f().can_import() and f().get_title() in DEFAULT_IMPORT_FORMATS]
 
    def save_model(self, request, obj, form, change):
        obj.person_slug = slugify_text_title(obj.person_first_name + ' ' + obj.person_last_name)   
        super(ImportExportModelAdmin, self).save_model(request, obj, form, change) 


class PersonContributionRoleAdmin(admin.ModelAdmin):
    list_display = ('contribution_role_role', 'contribution_role_id')

