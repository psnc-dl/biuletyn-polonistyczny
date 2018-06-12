# -*- coding: utf-8 -*-
from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from dal import autocomplete
from django import forms
from django.core.urlresolvers import reverse_lazy
from django.forms.widgets import Textarea
from django.utils.html import strip_tags
from django_addanother.widgets import AddAnotherWidgetWrapper
from extra_views.advanced import InlineFormSet

from bportal.module.common.fields import FieldBaseConfirm
from bportal.module.common.forms import NoHistoryBooleanField, BaseConfirmModelForm, HistoryTagField
from bportal.module.common.utils import remove_unnecessary_tags_from_title
from bportal.module.common.widgets import FileWidget

from .fields import FieldProject, FieldProjectFile, FieldProjectLink 
from .messages import MessageProject
from .models import Project, ProjectInstitution, ProjectParticipant, ProjectFile, ProjectLink, ProjectContentContribution


class AbstractProjectForm(forms.ModelForm):
    project_title = forms.CharField(label=FieldProject.TITLE, widget=CKEditorWidget(config_name='titles'))
    project_lead = forms.CharField(label=FieldProject.LEAD, widget=CKEditorWidget(config_name='leads'))
    project_image_copyright = forms.CharField(label=FieldProject.IMAGE_COPYRIGHT, widget=Textarea(attrs={'style' : 'height : auto', 'rows': 2}), required=False)
    project_description = forms.CharField(label=FieldProject.DESCRIPTION, widget=CKEditorUploadingWidget())
    project_keywords = HistoryTagField(label=FieldProject.KEYWORDS)
    
    def clean_project_date_end(self):   
        try:
            dateFrom = self.cleaned_data.get('project_date_start', None)
            dateTo = self.cleaned_data.get('project_date_end', None)
        except:
            raise forms.ValidationError(MessageProject.INCORRECT_DATE)
        if dateFrom is not None and dateTo is not None:
            if dateFrom > dateTo:
                raise forms.ValidationError(MessageProject.INCORRECT_PERIOD)
        return dateTo
        
    class Meta:
        abstract = True
        model = Project
        fields = ('__all__')
        widgets = {
            'project_targets': autocomplete.ModelSelect2Multiple(url='targetgroup-autocomplete'),
            'project_disciplines': autocomplete.ModelSelect2Multiple(url='researchdiscipline-autocomplete'),
            'project_connected_events' : autocomplete.ModelSelect2Multiple(url='event-autocomplete'),
            'project_connected_dissertations' : autocomplete.ModelSelect2Multiple(url='dissertation-autocomplete'),
            'project_connected_competitions' : autocomplete.ModelSelect2Multiple(url='competition-autocomplete'),
            'project_connected_joboffers' : autocomplete.ModelSelect2Multiple(url='joboffer-autocomplete'),
            'project_connected_eduoffers' : autocomplete.ModelSelect2Multiple(url='educationaloffer-autocomplete'),
            'project_connected_scholarships' : autocomplete.ModelSelect2Multiple(url='scholarship-autocomplete'),            
            'project_cities' : autocomplete.ModelSelect2Multiple(url='city-autocomplete'),
            }
        exclude = ('project_title_text', 'project_title_slug', 'project_institutions', 'project_participants', 'project_date_add', 'project_date_edit', 'project_added_by', 'project_modified_by', 'project_authorizations')
        

class ProjectAdminForm(AbstractProjectForm):
    force = NoHistoryBooleanField(label=FieldBaseConfirm.FORCE, required=False, initial=False, widget=forms.widgets.HiddenInput())
    
    class Meta(AbstractProjectForm.Meta):
        pass

        
class ProjectConfirmAdminForm(ProjectAdminForm):
        
    def clean(self):
        cleaned_data = super(ProjectConfirmAdminForm, self).clean()
        force = cleaned_data['force']
        if force is True:
            return cleaned_data
        if 'project_title' in cleaned_data:
            title = cleaned_data['project_title']
            title = remove_unnecessary_tags_from_title(title)
            title = strip_tags(title)             
            dup_list = Project.objects.filter(project_title_text=title)
            if dup_list:
                self.fields['force'].widget = forms.widgets.CheckboxInput()
                self.fields['force'].required = True
                self.fields['force'].initial = False
                raise forms.ValidationError(MessageProject.DUPLICATE)
        return cleaned_data
    
    class Meta(ProjectAdminForm.Meta):
        pass


class ProjectForm(AbstractProjectForm):
    project_image = forms.ImageField(label=FieldProject.IMAGE, widget=FileWidget(), required=False)
    project_date_start = forms.DateField(label=FieldProject.DATE_START, required=False, widget=forms.DateInput(attrs={'class': 'datepicker'}), input_formats=['%d.%m.%Y'])
    project_date_end = forms.DateField(label=FieldProject.DATE_END, required=False, widget=forms.DateInput(attrs={'class': 'datepicker'}), input_formats=['%d.%m.%Y'])
    project_financing = forms.CharField(label=FieldProject.FINANCING, required=False)
    project_support = forms.CharField(label=FieldProject.SUPPORT, required=False)
    
    class Meta(AbstractProjectForm.Meta):
        exclude = ('project_title_text', 'project_title_slug', 'project_institutions', 'project_participants', 'project_date_add', 'project_date_edit', 'project_added_by', 'project_modified_by', 'project_authorizations', 'project_is_promoted')

    class Media:
        # # they are not loaded by AddAnotherWidgetWrapper widget
        # # probably widget media do not work in inlines 
        # # force these media in the form        
        css = {
            'all': ('django_addanother/addanother.css',)
        }
        js = (
            'django_addanother/django_jquery.js',
            'admin/js/admin/RelatedObjectLookups.js',
        )

    
class ConfirmProjectForm(ProjectForm, BaseConfirmModelForm):
    pass


class ProjectParticipantAdminForm(forms.ModelForm):
    
    class Meta:
        model = ProjectParticipant
        widgets = {
            'person': autocomplete.ModelSelect2(url='person-autocomplete'),
            }
        exclude = ('project',)


class ProjectParticipantForm(forms.ModelForm):
    
    class Meta:
        model = ProjectParticipant
        widgets = {
            'person': AddAnotherWidgetWrapper(autocomplete.ModelSelect2(url='person-autocomplete'), reverse_lazy('person_create'),),
            }
        exclude = ('project',)


class ProjectParticipantInline(InlineFormSet):
    model = ProjectParticipant
    form_class = ProjectParticipantForm
    extra = 1


class ProjectInstitutionForm(forms.ModelForm):
   
    class Meta:
        model = ProjectInstitution
        widgets = {
            'institution': autocomplete.ModelSelect2(url='institution-autocomplete'),
            'role': autocomplete.Select2(attrs={'class': 'select2'}),            
            }
        exclude = ('project',)


class ProjectInstitutionInline(InlineFormSet):
    model = ProjectInstitution
    form_class = ProjectInstitutionForm
    extra = 1


class ProjectFileForm(forms.ModelForm):
    file = forms.FileField(label=FieldProjectFile.FILE, widget=FileWidget())
    copyright = forms.CharField(label=FieldProjectFile.COPYRIGHT, widget=Textarea(attrs={'style' : 'height : auto', 'rows': 2}), required=False)

    class Meta:
        model = ProjectFile
        exclude = ('project',)


class ProjectFileInline(InlineFormSet):
    model = ProjectFile
    form_class = ProjectFileForm
    extra = 1

        
class ProjectLinkForm(forms.ModelForm):
    link = forms.URLField(label=FieldProjectLink.LINK)

    class Meta:
        model = ProjectLink
        exclude = ('project',)


class ProjectLinkInline(InlineFormSet):
    model = ProjectLink
    form_class = ProjectLinkForm
    extra = 1
    

class ProjectContentContributionAdminForm(forms.ModelForm):
    
    class Meta:
        model = ProjectContentContribution
        widgets = {
            'person': autocomplete.ModelSelect2(url='person-autocomplete'),
            'role': autocomplete.Select2(attrs={'class': 'select2'}),
            }
        exclude = ('project',)


class ProjectContentContributionForm(forms.ModelForm):
    
    class Meta:
        model = ProjectContentContribution
        widgets = {
            'person': AddAnotherWidgetWrapper(autocomplete.ModelSelect2(url='person-autocomplete'), reverse_lazy('person_create'),),
            'role': autocomplete.Select2(attrs={'class': 'select2'}),
            }
        exclude = ('project',)


class ProjectContentContributionInline(InlineFormSet):
    model = ProjectContentContribution
    form_class = ProjectContentContributionForm
    extra = 1

