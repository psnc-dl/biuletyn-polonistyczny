# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils import timezone
from django.utils.html import strip_tags    
from import_export.admin import ImportExportModelAdmin
from reversion.admin import VersionAdmin

from bportal.account.profile.models import UserProfile
from bportal.module.common.storage import UtfImportExportStorage
from bportal.module.common.utils import remove_unnecessary_tags_from_title, slugify_text_title
from bportal.module.project.resources import ProjectResource
from bportal.settings import DEFAULT_IMPORT_FORMATS

from .forms import ProjectAdminForm, ProjectConfirmAdminForm, ProjectParticipantAdminForm, ProjectInstitutionForm, ProjectFileForm, ProjectLinkForm, ProjectContentContributionAdminForm
from .models import ProjectParticipant, ProjectInstitution, ProjectFile, ProjectLink, ProjectContentContribution, ProjectAuthorized, ProjectModification


class ProjectParticipantAdminInline(admin.TabularInline):
    model = ProjectParticipant
    form = ProjectParticipantAdminForm
    extra = 1


class ProjectInstitutionAdminInline(admin.TabularInline):
    model = ProjectInstitution
    form = ProjectInstitutionForm
    extra = 1

      
class ProjectFileAdminInline(admin.TabularInline):
    model = ProjectFile
    form = ProjectFileForm
    extra = 1


class ProjectLinkAdminInline(admin.TabularInline):
    model = ProjectLink
    form = ProjectLinkForm
    extra = 1


class ProjectContentContributionAdminInline(admin.TabularInline):
    model = ProjectContentContribution
    form = ProjectContentContributionAdminForm
    extra = 1    


class ProjectAdmin(ImportExportModelAdmin, VersionAdmin):
    list_display = ('project_title_safe', 'project_date_add', 'project_added_by', 'project_date_edit', 'project_modified_by',)
    inlines = (ProjectParticipantAdminInline, ProjectInstitutionAdminInline, ProjectFileAdminInline, ProjectLinkAdminInline, ProjectContentContributionAdminInline)
    form = ProjectAdminForm
    resource_class = ProjectResource
    search_fields = ('project_title_text',)
    list_filter = ('project_is_accepted', 'project_is_promoted')
    
    # : template for change_list view
    change_list_template = 'admin/import_export/change_list_import_export_projects.html'
    tmp_storage_class = UtfImportExportStorage
    from_encoding = 'utf-8'
    to_encoding = 'utf-8'
        
    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.form = ProjectAdminForm
        else:
            self.form = ProjectConfirmAdminForm
        return super(ProjectAdmin, self).get_form(request, obj, **kwargs)
    
    def get_import_formats(self):
        return [f for f in self.formats if f().can_import() and f().get_title() in DEFAULT_IMPORT_FORMATS]
    
    def save_model(self, request, obj, form, change):
        if obj.project_added_by is None:
            obj.project_added_by = request.user
        obj.project_modified_by = request.user
        obj.project_title = remove_unnecessary_tags_from_title(obj.project_title)
        obj.project_title_text = strip_tags(obj.project_title)          
        obj.project_title_slug = slugify_text_title(obj.project_title_text)
                  
        super(VersionAdmin, self).save_model(request, obj, form, change)
          
        modification = ProjectModification.objects.create(project=obj, user=request.user, date_time=timezone.now())
          
        profile = UserProfile.objects.get(user=request.user)
        authorized = ProjectAuthorized.objects.filter(project=obj);
        if not authorized.exists() :
            institutions = profile.user_institution.all()
            for institution in institutions:
                ProjectAuthorized.objects.create(project=obj, authorized=institution)
        profile.user_last_edit_date_time = modification.date_time
        profile.save()
