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
from bportal.module.project.models import Project

from .fields import FieldCompetition, FieldCompetitionFile, FieldCompetitionLink
from .messages import MessageCompetition
from .models import Competition, CompetitionFile, CompetitionLink, CompetitionContentContribution


class AbstractCompetitionForm(forms.ModelForm):
    competition_title = forms.CharField(label=FieldCompetition.TITLE, widget=CKEditorWidget(config_name='titles'))
    competition_lead = forms.CharField(label=FieldCompetition.LEAD, widget=CKEditorWidget(config_name='leads'))
    competition_image_copyright = forms.CharField(label=FieldCompetition.IMAGE_COPYRIGHT, widget=Textarea(attrs={'style' : 'height : auto', 'rows': 2}), required=False)
    competition_description = forms.CharField(label=FieldCompetition.DESCRIPTION, widget=CKEditorUploadingWidget())
    competition_keywords = HistoryTagField(label=FieldCompetition.KEYWORDS)
    competition_connected_projects = forms.ModelMultipleChoiceField(label=FieldCompetition.CONNECTED_PROJECTS, required=False, queryset=Project.objects.all(),
                                                              widget=autocomplete.ModelSelect2Multiple(url='project-autocomplete'))  # related_name field has to be defined in the form    

    def __init__(self, *args, **kwargs):
        if kwargs.get('instance'):
            initial = kwargs.setdefault('initial', {})
            # the widget for a ModelMultipleChoiceField expects a list of primary key for the selected data
            initial['competition_connected_projects'] = [project.project_id for project in kwargs['instance'].competition_connected_projects.all()]
        super(AbstractCompetitionForm, self).__init__(*args, **kwargs)  
        
    def _save_m2m(self):
        instance = self.instance
        instance.competition_connected_projects.clear()
        for project in self.cleaned_data['competition_connected_projects']:
            instance.competition_connected_projects.add(project)
        super(AbstractCompetitionForm, self)._save_m2m()       
    
    class Meta:
        abstract = True        
        model = Competition
        fields = ('__all__')
        widgets = {
            'competition_institutions': autocomplete.ModelSelect2Multiple(url='institution-autocomplete'),
            'competition_targets': autocomplete.ModelSelect2Multiple(url='targetgroup-autocomplete'),
            'competition_connected_events' : autocomplete.ModelSelect2Multiple(url='event-autocomplete'),               
            'competition_city' : autocomplete.ModelSelect2(url='city-autocomplete'),
        }
        exclude=('competition_title_text', 'competition_title_slug', 'competition_date_add', 'competition_date_edit', 'competition_added_by', 'competition_modified_by', 'competition_authorizations')



class CompetitionAdminForm(AbstractCompetitionForm):
    force = NoHistoryBooleanField(label=FieldBaseConfirm.FORCE, required=False, initial=False, widget=forms.widgets.HiddenInput())
    
    class Meta(AbstractCompetitionForm.Meta):
        pass
    

class CompetitionConfirmAdminForm(CompetitionAdminForm):
        
    def clean(self):
        cleaned_data = super(CompetitionConfirmAdminForm, self).clean()
        force = cleaned_data['force']
        if force:
            return cleaned_data
        if 'competition_title' in cleaned_data:
            title = cleaned_data['competition_title']
            title = remove_unnecessary_tags_from_title(title)
            title = strip_tags(title)
            dup_list = Competition.objects.filter(competition_title_text=title)
            if dup_list:
                self.fields['force'].widget = forms.widgets.CheckboxInput()
                self.fields['force'].required = True
                self.fields['force'].initial = False
                raise forms.ValidationError(MessageCompetition.DUPLICATE)
        return cleaned_data
    
    class Meta(CompetitionAdminForm.Meta):
        pass


class CompetitionForm(AbstractCompetitionForm):
    competition_image = forms.ImageField(label=FieldCompetition.IMAGE, widget=FileWidget(), required=False)
    competition_deadline_date = forms.DateField(label=FieldCompetition.DEADLINE_DATE, required=False, widget=forms.DateInput(attrs={'class': 'datepicker'}), input_formats=['%d.%m.%Y'])
    
    class Meta(AbstractCompetitionForm.Meta):    
        exclude=('competition_title_text', 'competition_title_slug', 'competition_date_add', 'competition_date_edit', 'competition_added_by', 'competition_modified_by', 'competition_authorizations', 'competition_is_promoted')

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


class ConfirmCompetitionForm(CompetitionForm, BaseConfirmModelForm):
    pass


class CompetitionFileForm(forms.ModelForm):
    file = forms.FileField(label=FieldCompetitionFile.FILE, widget=FileWidget())
    copyright = forms.CharField(label=FieldCompetitionFile.COPYRIGHT, widget=Textarea(attrs={'style' : 'height : auto', 'rows': 2}), required=False)

    class Meta:
        model = CompetitionFile
        exclude = ('competition',)


class CompetitionFileInline(InlineFormSet):
    model = CompetitionFile
    form_class = CompetitionFileForm
    extra = 1
    

class CompetitionLinkForm(forms.ModelForm):
    link = forms.URLField(label=FieldCompetitionLink.LINK)
    
    class Meta:
        model = CompetitionLink
        exclude = ('competition',)


class CompetitionLinkInline(InlineFormSet):
    model = CompetitionLink
    form_class = CompetitionLinkForm
    extra = 1


class CompetitionContentContributionAdminForm(forms.ModelForm):
    
    class Meta:
        model = CompetitionContentContribution
        widgets = {
            'person': autocomplete.ModelSelect2(url='person-autocomplete'),
            'role': autocomplete.Select2(attrs={'class': 'select2'}),
            }
        exclude = ('competition',)


class CompetitionContentContributionForm(forms.ModelForm):
    
    class Meta:
        model = CompetitionContentContribution
        widgets = {
            'person': AddAnotherWidgetWrapper(autocomplete.ModelSelect2(url='person-autocomplete'), reverse_lazy('person_create'),),
            'role': autocomplete.Select2(attrs={'class': 'select2'}),
            }
        exclude = ('competition',)


class CompetitionContentContributionInline(InlineFormSet):
    model = CompetitionContentContribution
    form_class = CompetitionContentContributionForm
    extra = 1
