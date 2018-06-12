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

from .fields import FieldScholarship, FieldScholarshipFile, FieldScholarshipLink
from .messages import MessageScholarship
from .models import Scholarship, ScholarshipType, ScholarshipFile, ScholarshipLink, ScholarshipContentContribution


class ScholarshipTypeAdminForm(forms.ModelForm):
    class Meta:
        model = ScholarshipType
        fields = ('__all__')


class AbstractScholarshipForm(forms.ModelForm):
    scholarship_name = forms.CharField(label=FieldScholarship.NAME, widget=CKEditorWidget(config_name='titles'))
    scholarship_lead = forms.CharField(label=FieldScholarship.LEAD, widget=CKEditorWidget(config_name='leads'))    
    scholarship_image_copyright = forms.CharField(label=FieldScholarship.IMAGE_COPYRIGHT, widget=Textarea(attrs={'style' : 'height : auto', 'rows': 2}), required=False)
    scholarship_description = forms.CharField(label=FieldScholarship.DESCRIPTION, widget=CKEditorUploadingWidget())
    scholarship_keywords = HistoryTagField(label=FieldScholarship.KEYWORDS)
    scholarship_connected_projects = forms.ModelMultipleChoiceField(label=FieldScholarship.CONNECTED_PROJECTS, required=False, queryset=Project.objects.all(),
                                                              widget=autocomplete.ModelSelect2Multiple(url='project-autocomplete'))  # related_name field has to be defined in the form    

    def __init__(self, *args, **kwargs):
        if kwargs.get('instance'):
            initial = kwargs.setdefault('initial', {})
            # the widget for a ModelMultipleChoiceField expects a list of primary key for the selected data
            initial['scholarship_connected_projects'] = [project.project_id for project in kwargs['instance'].scholarship_connected_projects.all()]
        super(AbstractScholarshipForm, self).__init__(*args, **kwargs) 
   
    def clean_scholarship_date_end(self):   
        try:
            dateFrom = self.cleaned_data.get('scholarship_date_start', None)
            dateTo = self.cleaned_data.get('scholarship_date_end', None)
        except:
            raise forms.ValidationError(MessageScholarship.INCORRECT_DATE)
        if dateFrom is not None and dateTo is not None:
            if dateFrom > dateTo:
                raise forms.ValidationError(MessageScholarship.INCORRECT_PERIOD)
        return dateTo
        
    def _save_m2m(self):
        instance = self.instance
        instance.scholarship_connected_projects.clear()
        for project in self.cleaned_data['scholarship_connected_projects']:
            instance.scholarship_connected_projects.add(project)
        super(AbstractScholarshipForm, self)._save_m2m()   
                
    class Meta:
        abstract = True            
        model = Scholarship
        fields = ('__all__')
        widgets = {
            'scholarship_founder': autocomplete.ModelSelect2(url='institution-autocomplete'),
            'scholarship_targets': autocomplete.ModelSelect2Multiple(url='targetgroup-autocomplete'),
            'scholarship_city' : autocomplete.ModelSelect2(url='city-autocomplete'),
            'scholarship_type': autocomplete.ModelSelect2(url='scholarshiptype-autocomplete'),
        }
        exclude = ('scholarship_name_text', 'scholarship_name_slug', 'scholarship_date_add', 'scholarship_date_edit', 'scholarship_added_by', 'scholarship_modified_by', 'scholarship_authorizations')



class ScholarshipAdminForm(AbstractScholarshipForm):
    force = NoHistoryBooleanField(label=FieldBaseConfirm.FORCE, required=False, initial=False, widget=forms.widgets.HiddenInput())
   
    class Meta(AbstractScholarshipForm.Meta):
        pass
    

class ScholarshipConfirmAdminForm(ScholarshipAdminForm):

    def clean(self):
        cleaned_data = super(ScholarshipConfirmAdminForm, self).clean()
        force = cleaned_data['force']
        if force:
            return cleaned_data
        if 'scholarship_name' in cleaned_data:
            name = cleaned_data['scholarship_name']
            name = remove_unnecessary_tags_from_title(name)
            name = strip_tags(name)                
            dup_list = Scholarship.objects.filter(scholarship_name=name)
            if dup_list:
                self.fields['force'].widget = forms.widgets.CheckboxInput()
                self.fields['force'].required = True
                self.fields['force'].initial = False
                raise forms.ValidationError(MessageScholarship.DUPLICATE)
        return cleaned_data
    
    class Meta(ScholarshipAdminForm.Meta):
        pass
    

class ScholarshipForm(AbstractScholarshipForm):
    scholarship_image = forms.ImageField(label=FieldScholarship.IMAGE, widget=FileWidget(), required=False)
    scholarship_date_start = forms.DateField(label=FieldScholarship.DATE_START, required=False, widget=forms.DateInput(attrs={'class': 'datepicker'}), input_formats=['%d.%m.%Y'])
    scholarship_date_end = forms.DateField(label=FieldScholarship.DATE_END, required=False, widget=forms.DateInput(attrs={'class': 'datepicker'}), input_formats=['%d.%m.%Y'])
        
    class Meta(AbstractScholarshipForm.Meta):   
        exclude = ('scholarship_name_text', 'scholarship_name_slug', 'scholarship_date_add', 'scholarship_date_edit', 'scholarship_added_by', 'scholarship_modified_by', 'scholarship_authorizations', 'scholarship_is_promoted')

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


class ConfirmScholarshipForm(ScholarshipForm, BaseConfirmModelForm):
    pass


class ScholarshipFileForm(forms.ModelForm):
    file = forms.FileField(label=FieldScholarshipFile.FILE, widget=FileWidget())
    copyright = forms.CharField(label=FieldScholarshipFile.COPYRIGHT, widget=Textarea(attrs={'style' : 'height : auto', 'rows': 2}), required=False)

    class Meta:
        model = ScholarshipFile
        exclude = ('scholarship',)


class ScholarshipFileInline(InlineFormSet):
    model = ScholarshipFile
    form_class = ScholarshipFileForm
    extra = 1


class ScholarshipLinkForm(forms.ModelForm):
    link = forms.URLField(label=FieldScholarshipLink.LINK)

    class Meta:
        model = ScholarshipLink
        exclude = ('scholarship',)


class ScholarshipLinkInline(InlineFormSet):
    model = ScholarshipLink
    form_class = ScholarshipLinkForm
    extra = 1


class ScholarshipContentContributionAdminForm(forms.ModelForm):
    
    class Meta:
        model = ScholarshipContentContribution
        widgets = {
            'person': autocomplete.ModelSelect2(url='person-autocomplete'),
            'role': autocomplete.Select2(attrs={'class': 'select2'}),
            }
        exclude = ('scholarship',)


class ScholarshipContentContributionForm(forms.ModelForm):
    
    class Meta:
        model = ScholarshipContentContribution
        widgets = {
            'person': AddAnotherWidgetWrapper(autocomplete.ModelSelect2(url='person-autocomplete'), reverse_lazy('person_create'),),
            'role': autocomplete.Select2(attrs={'class': 'select2'}),
            }
        exclude = ('scholarship',)


class ScholarshipContentContributionInline(InlineFormSet):
    model = ScholarshipContentContribution
    form_class = ScholarshipContentContributionForm
    extra = 1
    