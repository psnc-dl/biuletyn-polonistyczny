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

from .fields import FieldDissertation, FieldDissertationFile, FieldDissertationLink
from .messages import MessageDissertation
from .models import Dissertation, DissertationFile, DissertationLink, DissertationContentContribution


class AbstractDissertationForm(forms.ModelForm):
    dissertation_title = forms.CharField(label=FieldDissertation.TITLE, widget=CKEditorWidget(config_name='titles'))
    dissertation_lead = forms.CharField(label=FieldDissertation.LEAD, widget=CKEditorWidget(config_name='leads'))    
    dissertation_image_copyright = forms.CharField(label=FieldDissertation.IMAGE_COPYRIGHT, widget=Textarea(attrs={'style' : 'height : auto', 'rows': 2}), required=False)
    dissertation_description = forms.CharField(label=FieldDissertation.DESCRIPTION, widget=CKEditorUploadingWidget())
    dissertation_keywords = HistoryTagField(label=FieldDissertation.KEYWORDS)    
    dissertation_connected_projects = forms.ModelMultipleChoiceField(label=FieldDissertation.CONNECTED_PROJECTS, required=False, queryset=Project.objects.all(),
                                                              widget=autocomplete.ModelSelect2Multiple(url='project-autocomplete'))  # related_name field has to be defined in the form    
   
    def __init__(self, *args, **kwargs):
        if kwargs.get('instance'):
            initial = kwargs.setdefault('initial', {})
            # the widget for a ModelMultipleChoiceField expects a list of primary key for the selected data
            initial['dissertation_connected_projects'] = [project.project_id for project in kwargs['instance'].dissertation_connected_projects.all()]
        super(AbstractDissertationForm, self).__init__(*args, **kwargs)            
    
    def clean_dissertation_date_end(self):   
        try:
            dateFrom = self.cleaned_data.get('dissertation_date_start', None)
            dateTo = self.cleaned_data.get('dissertation_date_end', None)
        except:
            raise forms.ValidationError(MessageDissertation.INCORRECT_DATE)
        if dateFrom is not None and dateTo is not None:
            if dateFrom > dateTo:
                raise forms.ValidationError(MessageDissertation.INCORRECT_PERIOD)
        return dateTo

    def _save_m2m(self):
        instance = self.instance
        instance.dissertation_connected_projects.clear()
        for project in self.cleaned_data['dissertation_connected_projects']:
            instance.dissertation_connected_projects.add(project)
        super(AbstractDissertationForm, self)._save_m2m()      
        
    class Meta:
        abstract = True
        model = Dissertation
        fields = ('__all__')
        widgets = {
            'dissertation_institution': autocomplete.ModelSelect2(url='institution-autocomplete'),
            'dissertation_supervisors': autocomplete.ModelSelect2Multiple(url='person-autocomplete'),
            'dissertation_author': autocomplete.ModelSelect2(url='person-autocomplete'),
            'dissertation_reviewers': autocomplete.ModelSelect2Multiple(url='person-autocomplete'),
            'dissertation_connected_events' : autocomplete.ModelSelect2Multiple(url='event-autocomplete'),
            'dissertation_city': autocomplete.ModelSelect2(url='city-autocomplete'),
            'dissertation_disciplines': autocomplete.ModelSelect2Multiple(url='researchdiscipline-autocomplete'),
            'dissertation_type': autocomplete.Select2(attrs={'class': 'select2'}),
            }
        exclude = ('dissertation_title_text', 'dissertation_title_slug', 'dissertation_date_add', 'dissertation_date_edit', 'dissertation_added_by', 'dissertation_modified_by', 'dissertation_authorizations')
        

class DissertationAdminForm(AbstractDissertationForm):
    force = NoHistoryBooleanField(label=FieldBaseConfirm.FORCE, required=False, initial=False, widget=forms.widgets.HiddenInput())
    
    class Meta(AbstractDissertationForm.Meta):
        pass
    

class DissertationConfirmAdminForm(DissertationAdminForm):
    
    def clean(self):
        cleaned_data = super(DissertationConfirmAdminForm, self).clean()
        force = cleaned_data['force']
        if force:
            return cleaned_data
        if 'dissertation_title' in cleaned_data:        
            title = cleaned_data['dissertation_title']
            title = remove_unnecessary_tags_from_title(title)
            title = strip_tags(title)
            dup_list = Dissertation.objects.filter(dissertation_title=title)
            if dup_list:
                self.fields['force'].widget = forms.widgets.CheckboxInput()
                self.fields['force'].required = True
                self.fields['force'].initial = False
                raise forms.ValidationError(MessageDissertation.DUPLICATE)
        return cleaned_data
        
    class Meta(DissertationAdminForm.Meta):
        pass


class DissertationForm(AbstractDissertationForm):
    dissertation_image = forms.FileField(label=FieldDissertation.IMAGE, widget=FileWidget(), required=False)
    dissertation_date_start = forms.DateField(label=FieldDissertation.DATE_START, required=False, widget=forms.DateInput(attrs={'class': 'datepicker'}), input_formats=['%d.%m.%Y'])
    dissertation_date_end = forms.DateField(label=FieldDissertation.DATE_END, required=False, widget=forms.DateInput(attrs={'class': 'datepicker'}), input_formats=['%d.%m.%Y'])
    dissertation_file = forms.FileField(label=FieldDissertation.FILE, widget=FileWidget(), required=False)
    
    class Meta(AbstractDissertationForm.Meta):
        widgets = {
            'dissertation_institution': autocomplete.ModelSelect2(url='institution-autocomplete'),
            'dissertation_supervisors': AddAnotherWidgetWrapper(autocomplete.ModelSelect2Multiple(url='person-autocomplete'), reverse_lazy('person_create'),),
            'dissertation_author': AddAnotherWidgetWrapper(autocomplete.ModelSelect2(url='person-autocomplete'), reverse_lazy('person_create'),),
            'dissertation_reviewers': AddAnotherWidgetWrapper(autocomplete.ModelSelect2Multiple(url='person-autocomplete'), reverse_lazy('person_create'),),
            'dissertation_connected_events' : autocomplete.ModelSelect2Multiple(url='event-autocomplete'),
            'dissertation_city': autocomplete.ModelSelect2(url='city-autocomplete'),
            'dissertation_disciplines': autocomplete.ModelSelect2Multiple(url='researchdiscipline-autocomplete'),
            'dissertation_type': autocomplete.Select2(attrs={'class': 'select2'}),
            }
        exclude = ('dissertation_title_text', 'dissertation_title_slug', 'dissertation_date_add', 'dissertation_date_edit', 'dissertation_added_by', 'dissertation_modified_by', 'dissertation_authorizations', 'dissertation_is_promoted')


class ConfirmDissertationForm(DissertationForm, BaseConfirmModelForm):
    pass


class DissertationFileForm(forms.ModelForm):
    file = forms.FileField(label=FieldDissertationFile.FILE, widget=FileWidget())
    copyright = forms.CharField(label=FieldDissertationFile.COPYRIGHT, widget=Textarea(attrs={'style' : 'height : auto', 'rows': 2}), required=False)

    class Meta:
        model = DissertationFile
        exclude = ('dissertation',)


class DissertationFileInline(InlineFormSet):
    model = DissertationFile
    form_class = DissertationFileForm
    extra = 1
    

class DissertationLinkForm(forms.ModelForm):
    link = forms.URLField(label=FieldDissertationLink.LINK)
    
    class Meta:
        model = DissertationLink
        exclude = ('dissertation',)


class DissertationLinkInline(InlineFormSet):
    model = DissertationLink
    form_class = DissertationLinkForm
    extra = 1


class DissertationContentContributionAdminForm(forms.ModelForm):
    
    class Meta:
        model = DissertationContentContribution
        widgets = {
            'person': autocomplete.ModelSelect2(url='person-autocomplete'),
            'role': autocomplete.Select2(attrs={'class': 'select2'}),
            }
        exclude = ('dissertation',)


class DissertationContentContributionForm(forms.ModelForm):
    
    class Meta:
        model = DissertationContentContribution
        widgets = {
            'person': AddAnotherWidgetWrapper(autocomplete.ModelSelect2(url='person-autocomplete'), reverse_lazy('person_create'),),
            'role': autocomplete.Select2(attrs={'class': 'select2'}),
            }
        exclude = ('dissertation',)


class DissertationContentContributionInline(InlineFormSet):
    model = DissertationContentContribution
    form_class = DissertationContentContributionForm
    extra = 1
