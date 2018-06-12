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

from .fields import FieldEducationalOffer, FieldEducationalOfferFile, FieldEducationalOfferLink
from .messages import MessageEducationalOffer
from .models import EducationalOfferMode, EducationalOfferType, EducationalOffer, EducationalOfferFile, EducationalOfferLink, EducationalOfferContentContribution


class EducationalOfferModeAdminForm(forms.ModelForm):
    class Meta:
        model = EducationalOfferMode
        fields = ('__all__')


class EducationalOfferTypeAdminForm(forms.ModelForm):
    class Meta:
        model = EducationalOfferType
        fields = ('__all__')
     
     
class AbstractEducationalOfferForm(forms.ModelForm):
    eduoffer_position = forms.CharField(label=FieldEducationalOffer.POSITION, widget=CKEditorWidget(config_name='titles'))
    eduoffer_lead = forms.CharField(label=FieldEducationalOffer.LEAD, widget=CKEditorWidget(config_name='leads'))    
    eduoffer_image_copyright = forms.CharField(label=FieldEducationalOffer.IMAGE_COPYRIGHT, widget=Textarea(attrs={'style' : 'height : auto', 'rows': 2}), required=False)
    eduoffer_description = forms.CharField(label=FieldEducationalOffer.DESCRIPTION, widget=CKEditorUploadingWidget())
    eduoffer_keywords = HistoryTagField(label=FieldEducationalOffer.KEYWORDS)    
    eduoffer_connected_projects = forms.ModelMultipleChoiceField(label=FieldEducationalOffer.CONNECTED_PROJECTS, required=False, queryset=Project.objects.all(),
                                                              widget=autocomplete.ModelSelect2Multiple(url='project-autocomplete'))  # related_name field has to be defined in the form    
 
    def __init__(self, *args, **kwargs):
        if kwargs.get('instance'):
            initial = kwargs.setdefault('initial', {})
            # the widget for a ModelMultipleChoiceField expects a list of primary key for the selected data
            initial['eduoffer_connected_projects'] = [project.project_id for project in kwargs['instance'].eduoffer_connected_projects.all()]
        super(AbstractEducationalOfferForm, self).__init__(*args, **kwargs) 
        
    def clean_eduoffer_date_end(self):   
        try:
            dateFrom = self.cleaned_data.get('eduoffer_date_start', None)
            dateTo = self.cleaned_data.get('eduoffer_date_end', None)
        except:
            raise forms.ValidationError(MessageEducationalOffer.INCORRECT_DATE)
        if dateFrom is not None and dateTo is not None:
            if dateFrom > dateTo:
                raise forms.ValidationError(MessageEducationalOffer.INCORRECT_PERIOD)
        return dateTo

    def _save_m2m(self):
        instance = self.instance
        instance.eduoffer_connected_projects.clear()
        for project in self.cleaned_data['eduoffer_connected_projects']:
            instance.eduoffer_connected_projects.add(project)
        super(AbstractEducationalOfferForm, self)._save_m2m()        
         
    class Meta:
        abstract = True        
        model = EducationalOffer
        fields = ('__all__')
        widgets = {
            'eduoffer_institution': autocomplete.ModelSelect2(url='institution-autocomplete'),
            'eduoffer_city' : autocomplete.ModelSelect2(url='city-autocomplete'),
            'eduoffer_type' : autocomplete.ModelSelect2(url='educationaloffertype-autocomplete'),
            'eduoffer_mode' : autocomplete.ModelSelect2(url='educationaloffermode-autocomplete'),
        }
        exclude=('eduoffer_position_text', 'eduoffer_position_slug', 'eduoffer_date_add', 'eduoffer_date_edit', 'eduoffer_added_by', 'eduoffer_modified_by', 'eduoffer_authorizations')
        

class EducationalOfferAdminForm(AbstractEducationalOfferForm):
    force = NoHistoryBooleanField(label=FieldBaseConfirm.FORCE, required=False, initial=False, widget=forms.widgets.HiddenInput())
         
    class Meta(AbstractEducationalOfferForm.Meta):
        pass


class EducationalOfferConfirmAdminForm(EducationalOfferAdminForm):
    
    def clean(self):
        cleaned_data = super(EducationalOfferConfirmAdminForm, self).clean()
        force = cleaned_data['force']
        if force:
            return cleaned_data
        if 'eduoffer_position' in cleaned_data:        
            position = cleaned_data['eduoffer_position']
            position = remove_unnecessary_tags_from_title(position)
            position = strip_tags(position)            
            dup_list = EducationalOffer.objects.filter(eduoffer_position_text=position)
            if dup_list:
                self.fields['force'].widget = forms.widgets.CheckboxInput()
                self.fields['force'].required = True
                self.fields['force'].initial = False
                raise forms.ValidationError(MessageEducationalOffer.DUPLICATE)
        return cleaned_data
    
    class Meta(EducationalOfferAdminForm.Meta):
        pass
    

class EducationalOfferForm(AbstractEducationalOfferForm):
    eduoffer_image = forms.FileField(label=FieldEducationalOffer.IMAGE, widget=FileWidget(), required=False)
    eduoffer_date_start = forms.DateField(label=FieldEducationalOffer.DATE_START, required=False, widget=forms.DateInput(attrs={'class': 'datepicker'}), input_formats=['%d.%m.%Y'])
    eduoffer_date_end = forms.DateField(label=FieldEducationalOffer.DATE_END, required=False, widget=forms.DateInput(attrs={'class': 'datepicker'}), input_formats=['%d.%m.%Y'])
     
    class Meta(AbstractEducationalOfferForm.Meta):   
        exclude=('eduoffer_position_text', 'eduoffer_position_slug', 'eduoffer_date_add', 'eduoffer_date_edit', 'eduoffer_added_by', 'eduoffer_modified_by', 'eduoffer_authorizations', 'eduoffer_is_promoted')

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
        

class ConfirmEducationalOfferForm(EducationalOfferForm, BaseConfirmModelForm):
    pass


class EducationalOfferFileForm(forms.ModelForm):
    file = forms.FileField(label=FieldEducationalOfferFile.FILE, widget=FileWidget())
    copyright = forms.CharField(label=FieldEducationalOfferFile.COPYRIGHT, widget=Textarea(attrs={'style' : 'height : auto', 'rows': 2}), required=False)
    
    class Meta:
        model = EducationalOfferFile
        exclude = ('eduoffer',)
         
         
class EducationalOfferFileInline(InlineFormSet):
    model = EducationalOfferFile
    form_class = EducationalOfferFileForm
    extra = 1


class EducationalOfferLinkForm(forms.ModelForm):
    link = forms.URLField(label=FieldEducationalOfferLink.LINK)
    
    class Meta:
        model = EducationalOfferLink
        exclude = ('eduoffer',)


class EducationalOfferLinkInline(InlineFormSet):
    model = EducationalOfferLink
    form_class = EducationalOfferLinkForm
    extra = 1


class EducationalOfferContentContributionAdminForm(forms.ModelForm):
    
    class Meta:
        model = EducationalOfferContentContribution
        widgets = {
            'person': autocomplete.ModelSelect2(url='person-autocomplete'),
            'role': autocomplete.Select2(attrs={'class': 'select2'}),
            }
        exclude = ('eduoffer',)


class EducationalOfferContentContributionForm(forms.ModelForm):
    
    class Meta:
        model = EducationalOfferContentContribution
        widgets = {
            'person': AddAnotherWidgetWrapper(autocomplete.ModelSelect2(url='person-autocomplete'), reverse_lazy('person_create'),),
            'role': autocomplete.Select2(attrs={'class': 'select2'}),
            }
        exclude = ('eduoffer',)


class EducationalOfferContentContributionInline(InlineFormSet):
    model = EducationalOfferContentContribution
    form_class = EducationalOfferContentContributionForm
    extra = 1
