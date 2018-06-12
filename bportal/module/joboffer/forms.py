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

from .fields import FieldJobOffer, FieldJobOfferFile, FieldJobOfferLink
from .messages import MessageJobOffer
from .models import JobOfferDiscipline, JobOfferType, JobOffer, JobOfferFile, JobOfferLink, JobOfferContentContribution


class JobOfferDisciplineAdminForm(forms.ModelForm):
    class Meta:
        model = JobOfferDiscipline
        fields = ('__all__')
        

class JobOfferTypeAdminForm(forms.ModelForm):
    class Meta:
        model = JobOfferType
        fields = ('__all__')


class AbstractJobOfferForm(forms.ModelForm):
    joboffer_position = forms.CharField(label=FieldJobOffer.POSITION, widget=CKEditorWidget(config_name='titles'))
    joboffer_lead = forms.CharField(label=FieldJobOffer.LEAD, widget=CKEditorWidget(config_name='leads'))
    joboffer_image_copyright = forms.CharField(label=FieldJobOffer.IMAGE_COPYRIGHT, widget=Textarea(attrs={'style' : 'height : auto', 'rows': 2}), required=False)
    joboffer_description = forms.CharField(label=FieldJobOffer.DESCRIPTION, widget=CKEditorUploadingWidget())
    joboffer_keywords = HistoryTagField(label=FieldJobOffer.KEYWORDS)
    joboffer_connected_projects = forms.ModelMultipleChoiceField(label=FieldJobOffer.CONNECTED_PROJECTS, required=False, queryset=Project.objects.all(),
                                                              widget=autocomplete.ModelSelect2Multiple(url='project-autocomplete'))  # related_name field has to be defined in the form    

    def __init__(self, *args, **kwargs):
        if kwargs.get('instance'):
            initial = kwargs.setdefault('initial', {})
            # the widget for a ModelMultipleChoiceField expects a list of primary key for the selected data
            initial['joboffer_connected_projects'] = [project.project_id for project in kwargs['instance'].joboffer_connected_projects.all()]
        super(AbstractJobOfferForm, self).__init__(*args, **kwargs)  
        
    def clean_joboffer_date_end(self):   
        try:
            dateFrom = self.cleaned_data.get('joboffer_date_start', None)
            dateTo = self.cleaned_data.get('joboffer_date_end', None)
        except:
            raise forms.ValidationError(MessageJobOffer.INCORRECT_DATE)
        if dateFrom is not None and dateTo is not None:
            if dateFrom > dateTo:
                raise forms.ValidationError(MessageJobOffer.INCORRECT_PERIOD)
        return dateTo

    def _save_m2m(self):
        instance = self.instance
        instance.joboffer_connected_projects.clear()
        for project in self.cleaned_data['joboffer_connected_projects']:
            instance.joboffer_connected_projects.add(project)
        super(AbstractJobOfferForm, self)._save_m2m()    

    
    class Meta:
        abstract = True
        model = JobOffer
        fields = ('__all__')
        widgets = {
            'joboffer_institution': autocomplete.ModelSelect2(url='institution-autocomplete'),
            'joboffer_type' : autocomplete.ModelSelect2(url='joboffertype-autocomplete'),
            'joboffer_disciplines' : autocomplete.ModelSelect2Multiple(url='jobofferdiscipline-autocomplete'),
            'joboffer_cities' : autocomplete.ModelSelect2Multiple(url='city-autocomplete'),
        }
        exclude = ('joboffer_position_text', 'joboffer_position_slug', 'joboffer_date_add', 'joboffer_date_edit', 'joboffer_added_by', 'joboffer_modified_by', 'joboffer_authorizations')
                

class JobOfferAdminForm(AbstractJobOfferForm):
    force = NoHistoryBooleanField(label=FieldBaseConfirm.FORCE, required=False, initial=False, widget=forms.widgets.HiddenInput())
    
    class Meta(AbstractJobOfferForm.Meta):
        pass


class JobOfferConfirmAdminForm(JobOfferAdminForm):
    
    def clean(self):
        cleaned_data = super(JobOfferConfirmAdminForm, self).clean()
        force = cleaned_data['force']
        if force:
            return cleaned_data
        if 'joboffer_position' in cleaned_data:
            position = cleaned_data['joboffer_position']
            position = remove_unnecessary_tags_from_title(position)
            position = strip_tags(position)               
            dup_list = JobOffer.objects.filter(joboffer_position_text=position)
            if dup_list:
                self.fields['force'].widget = forms.widgets.CheckboxInput()
                self.fields['force'].required = True
                self.fields['force'].initial = False
                raise forms.ValidationError(MessageJobOffer.DUPLICATE)
        return cleaned_data
    
    class Meta(JobOfferAdminForm.Meta):
        pass

     
class JobOfferForm(AbstractJobOfferForm):
    joboffer_image = forms.FileField(label=FieldJobOffer.IMAGE, widget=FileWidget(), required=False)
    joboffer_date_start = forms.DateField(label=FieldJobOffer.DATE_START, required=False, widget=forms.DateInput(attrs={'class': 'datepicker'}), input_formats=['%d.%m.%Y'])
    joboffer_date_end = forms.DateField(label=FieldJobOffer.DATE_END, required=False, widget=forms.DateInput(attrs={'class': 'datepicker'}), input_formats=['%d.%m.%Y'])
        
    class Meta(AbstractJobOfferForm.Meta):   
        exclude = ('joboffer_position_text', 'joboffer_position_slug', 'joboffer_date_add', 'joboffer_date_edit', 'joboffer_added_by', 'joboffer_modified_by', 'joboffer_authorizations', 'joboffer_is_promoted')

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
        

class ConfirmJobOfferForm(JobOfferForm, BaseConfirmModelForm):
    pass


class JobOfferFileForm(forms.ModelForm):
    file = forms.FileField(label=FieldJobOfferFile.FILE, widget=FileWidget())
    copyright = forms.CharField(label=FieldJobOfferFile.COPYRIGHT, widget=Textarea(attrs={'style' : 'height : auto', 'rows': 2}), required=False)
    
    class Meta:
        model = JobOfferFile
        exclude = ('joboffer',)
        

class JobOfferFileInline(InlineFormSet):
    model = JobOfferFile
    form_class = JobOfferFileForm
    extra = 1


class JobOfferLinkForm(forms.ModelForm):
    link = forms.URLField(label=FieldJobOfferLink.LINK)
    
    class Meta:
        model = JobOfferLink
        exclude = ('joboffer',)


class JobOfferLinkInline(InlineFormSet):
    model = JobOfferLink
    form_class = JobOfferLinkForm
    extra = 1


class JobOfferContentContributionAdminForm(forms.ModelForm):
    
    class Meta:
        model = JobOfferContentContribution
        widgets = {
            'person': autocomplete.ModelSelect2(url='person-autocomplete'),
            'role': autocomplete.Select2(attrs={'class': 'select2'}),
            }
        exclude = ('joboffer',)


class JobOfferContentContributionForm(forms.ModelForm):
    
    class Meta:
        model = JobOfferContentContribution
        widgets = {
            'person': AddAnotherWidgetWrapper(autocomplete.ModelSelect2(url='person-autocomplete'), reverse_lazy('person_create'),),
            'role': autocomplete.Select2(attrs={'class': 'select2'}),
            }
        exclude = ('joboffer',)


class JobOfferContentContributionInline(InlineFormSet):
    model = JobOfferContentContribution
    form_class = JobOfferContentContributionForm
    extra = 1
