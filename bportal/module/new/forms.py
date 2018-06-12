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

from .fields import FieldNew, FieldNewFile, FieldNewLink
from .messages import MessageNew
from .models import NewCategory, New, NewFile, NewLink, NewContentContribution


class NewCategoryAdminForm(forms.ModelForm):            
    class Meta:
        model = NewCategory
        fields = ('__all__')
        

class AbstractNewForm(forms.ModelForm):
    new_title = forms.CharField(label=FieldNew.TITLE, widget=CKEditorWidget(config_name='titles'))
    new_lead = forms.CharField(label=FieldNew.LEAD, widget=CKEditorWidget(config_name='leads'))
    new_image_copyright = forms.CharField(label=FieldNew.IMAGE_COPYRIGHT, widget=Textarea(attrs={'style' : 'height : auto', 'rows': 2}), required=False)
    new_description = forms.CharField(label=FieldNew.DESCRIPTION, widget=CKEditorUploadingWidget(), required=False)  
    new_keywords = HistoryTagField(label=FieldNew.KEYWORDS, required=False)
    
    class Meta:
        abstract = True
        model = New
        fields = ('__all__')
        widgets = {
            'new_category': autocomplete.ModelSelect2(url='newcategory-autocomplete'),
            'new_related_event' : autocomplete.ModelSelect2(url='event-autocomplete', attrs={'class' : 'alamamkota'}),
            'new_related_project' : autocomplete.ModelSelect2(url='project-autocomplete'),
            'new_related_dissertation' : autocomplete.ModelSelect2(url='dissertation-autocomplete'),
            'new_related_competition' : autocomplete.ModelSelect2(url='competition-autocomplete'),
            'new_related_joboffer' : autocomplete.ModelSelect2(url='joboffer-autocomplete'),
            'new_related_eduoffer' : autocomplete.ModelSelect2(url='educationaloffer-autocomplete'),
            'new_related_scholarship' : autocomplete.ModelSelect2(url='scholarship-autocomplete'),
            'new_related_book' : autocomplete.ModelSelect2(url='book-autocomplete'),
            'new_related_article' : autocomplete.ModelSelect2(url='article-autocomplete'),
            'new_related_journalissue' : autocomplete.ModelSelect2(url='journalissue-autocomplete'),
            }
        exclude = ('new_title_text', 'new_title_slug', 'new_date_add', 'new_date_edit', 'new_added_by', 'new_modified_by', 'new_authorizations', 'new_contributors')


class NewAdminForm(AbstractNewForm):
    force = NoHistoryBooleanField(label=FieldBaseConfirm.FORCE, required=False, initial=False, widget=forms.widgets.HiddenInput())
    
    class Meta(AbstractNewForm.Meta):
        pass


class NewConfirmAdminForm(NewAdminForm):
        
    def clean(self):
        cleaned_data = super(NewConfirmAdminForm, self).clean()
        force = cleaned_data['force']
        if force is True:
            return cleaned_data
        if 'new_title' in cleaned_data:
            title = cleaned_data['new_title']
            title = remove_unnecessary_tags_from_title(title)
            title = strip_tags(title)             
            dup_list = New.objects.filter(new_title_text=title)
            if dup_list:
                self.fields['force'].widget = forms.widgets.CheckboxInput()
                self.fields['force'].required = True
                self.fields['force'].initial = False
                raise forms.ValidationError(MessageNew.DUPLICATE)
        return cleaned_data
    
    class Meta(NewAdminForm.Meta):
        pass


class NewForm(AbstractNewForm):
    new_image = forms.ImageField(label=FieldNew.IMAGE, widget=FileWidget(), required=False)
    
    class Meta(AbstractNewForm.Meta):
        exclude = ('new_title_text', 'new_title_slug', 'new_date_add', 'new_date_edit', 'new_added_by', 'new_modified_by', 'new_authorizations', 'new_is_promoted', 'new_contributors')

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


class ConfirmNewForm(NewForm, BaseConfirmModelForm):
    pass


class NewFileForm(forms.ModelForm):
    file = forms.FileField(label=FieldNewFile.FILE, widget=FileWidget())
    copyright = forms.CharField(label=FieldNewFile.COPYRIGHT, widget=Textarea(attrs={'style' : 'height : auto', 'rows': 2}), required=False)

    class Meta:
        model = NewFile
        exclude = ('new',)


class NewFileInline(InlineFormSet):
    model = NewFile
    form_class = NewFileForm
    extra = 1

        
class NewLinkForm(forms.ModelForm):
    link = forms.URLField(label=FieldNewLink.LINK)

    class Meta:
        model = NewLink
        exclude = ('new',)


class NewLinkInline(InlineFormSet):
    model = NewLink
    form_class = NewLinkForm
    extra = 1
    

class NewContentContributionAdminForm(forms.ModelForm):
    
    class Meta:
        model = NewContentContribution
        widgets = {
            'person': autocomplete.ModelSelect2(url='person-autocomplete'),
            'role': autocomplete.Select2(attrs={'class': 'select2'}),
            }
        exclude = ('new',)


class NewContentContributionForm(forms.ModelForm):
    
    class Meta:
        model = NewContentContribution
        widgets = {
            'person': AddAnotherWidgetWrapper(autocomplete.ModelSelect2(url='person-autocomplete'), reverse_lazy('person_create'),),
            'role': autocomplete.Select2(attrs={'class': 'select2'}),
            }
        exclude = ('new',)


class NewContentContributionInline(InlineFormSet):
    model = NewContentContribution
    form_class = NewContentContributionForm
    extra = 1

