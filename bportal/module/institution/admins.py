# -*- coding: utf-8 -*-
from django.contrib import admin
from reversion.admin import VersionAdmin

from bportal.module.common.utils import slugify_text_title
from bportal.module.institution.fields import FieldInstitution

from .forms import InstitutionAdminForm, InstitutionConfirmAdminForm
from .models import InstitutionType, InstitutionRole


class InstitutionTypeAdmin(admin.ModelAdmin):
    list_display = ('type_name',)
    model = InstitutionType


class InstitutionAdmin(VersionAdmin):
    list_display = ('get_institution_name', 'institution_parent', 'institution_type', 'institution_city')
    form = InstitutionAdminForm
    search_fields = ('institution_fullname', 'institution_shortname',)
     
    def get_institution_name(self, obj):
        return str(obj)
    
    get_institution_name.short_description = FieldInstitution.FULLNAME
    get_institution_name.admin_order_field = 'institution_fullname'
    
    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.form = InstitutionAdminForm
        else:
            self.form = InstitutionConfirmAdminForm
        return super(InstitutionAdmin, self).get_form(request, obj, **kwargs)
    
    def save_model(self, request, obj, form, change):
        obj.institution_slug = slugify_text_title(obj.institution_shortname)   
        super(VersionAdmin, self).save_model(request, obj, form, change)
 
     
class InstitutionRoleAdmin(admin.ModelAdmin):
    list_display = ('institution_role_role',)
    model = InstitutionRole
