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
from bportal.module.journal.fields import FieldJournal
from bportal.module.journal.models import Journal

from .fields import FieldJournalIssue, FieldJournalIssueFile, FieldJournalIssueLink 
from .messages import MessageJournalIssue
from .models import JournalIssue, JournalIssueFile, JournalIssueLink, JournalIssueContentContribution


class AbstractJournalForm(forms.ModelForm):
    journal_title = forms.CharField(label=FieldJournal.TITLE, widget=CKEditorWidget(config_name='titles'))
    journal_lead = forms.CharField(label=FieldJournal.LEAD, widget=CKEditorWidget(config_name='leads'))
    
    class Meta:
        abstract = True
        model = Journal
        fields = ('__all__')
        widgets = {
            'journal_categories': autocomplete.ModelSelect2Multiple(url='publicationcategory-autocomplete'),
            'journal_editor_in_chief': autocomplete.ModelSelect2(url='person-autocomplete'),
            'journal_publisher' : autocomplete.ModelSelect2(url='institution-autocomplete'),
            }
        exclude = ('journal_title_text', 'journal_title_slug',)
        
        
class JournalAdminForm(AbstractJournalForm):
    force = NoHistoryBooleanField(label=FieldBaseConfirm.FORCE, required=False, initial=False, widget=forms.widgets.HiddenInput())
    
    class Meta(AbstractJournalForm.Meta):
        pass

class JournalConfirmAdminForm(JournalAdminForm):
        
    def clean(self):
        cleaned_data = super(JournalConfirmAdminForm, self).clean()
        force = cleaned_data['force']
        if force is True:
            return cleaned_data
        if 'journal_title' in cleaned_data:
            title = cleaned_data['journal_title']
            title = remove_unnecessary_tags_from_title(title)
            title = strip_tags(title)             
            dup_list = JournalIssue.objects.filter(journalissue_title_text=title)
            if dup_list:
                self.fields['force'].widget = forms.widgets.CheckboxInput()
                self.fields['force'].required = True
                self.fields['force'].initial = False
                raise forms.ValidationError(MessageJournalIssue.DUPLICATE)
        return cleaned_data
    
    class Meta(JournalAdminForm.Meta):
        pass
       
class AbstractJournalIssueForm(forms.ModelForm):
    journalissue_title = forms.CharField(label=FieldJournalIssue.TITLE, widget=CKEditorWidget(config_name='titles'))
    journalissue_lead = forms.CharField(label=FieldJournalIssue.LEAD, widget=CKEditorWidget(config_name='leads'))
    journalissue_image_copyright = forms.CharField(label=FieldJournalIssue.IMAGE_COPYRIGHT, widget=Textarea(attrs={'style' : 'height : auto', 'rows': 2}), required=False)
    journalissue_description = forms.CharField(label=FieldJournalIssue.DESCRIPTION, widget=CKEditorUploadingWidget())  
    journalissue_table_of_contents = forms.CharField(label=FieldJournalIssue.TABLE_OF_CONTENTS, widget=CKEditorWidget(), required=False)
    journalissue_keywords = HistoryTagField(label=FieldJournalIssue.KEYWORDS)
    
    class Meta:
        abstract = True
        model = JournalIssue
        fields = ('__all__')
        widgets = {
            'journalissue_category': autocomplete.ModelSelect2(url='publicationcategory-autocomplete'),
            'journalissue_publisher' : autocomplete.ModelSelect2(url='institution-autocomplete'),
            'journalissue_journal' : autocomplete.ModelSelect2(url='journal-autocomplete'),
            }
        exclude = ('journalissue_title_text', 'journalissue_title_slug', 'journalissue_date_add', 'journalissue_date_edit', 'journalissue_added_by', 'journalissue_modified_by', 'journalissue_authorizations')
        

class JournalIssueAdminForm(AbstractJournalIssueForm):
    force = NoHistoryBooleanField(label=FieldBaseConfirm.FORCE, required=False, initial=False, widget=forms.widgets.HiddenInput())
    
    class Meta(AbstractJournalIssueForm.Meta):
        pass

        
class JournalIssueConfirmAdminForm(JournalIssueAdminForm):
        
    def clean(self):
        cleaned_data = super(JournalIssueConfirmAdminForm, self).clean()
        force = cleaned_data['force']
        if force is True:
            return cleaned_data
        if 'journalissue_title' in cleaned_data:
            title = cleaned_data['journalissue_title']
            title = remove_unnecessary_tags_from_title(title)
            title = strip_tags(title)             
            dup_list = JournalIssue.objects.filter(journalissue_title_text=title)
            if dup_list:
                self.fields['force'].widget = forms.widgets.CheckboxInput()
                self.fields['force'].required = True
                self.fields['force'].initial = False
                raise forms.ValidationError(MessageJournalIssue.DUPLICATE)
        return cleaned_data
    
    class Meta(JournalIssueAdminForm.Meta):
        pass


class JournalIssueForm(AbstractJournalIssueForm):
    journalissue_image = forms.ImageField(label=FieldJournalIssue.IMAGE, widget=FileWidget(), required=False)
    journalissue_issn = forms.CharField(label=FieldJournalIssue.ISSN, required=False)
    journalissue_year = forms.CharField(label=FieldJournalIssue.YEAR, required=False)
    journalissue_volume = forms.CharField(label=FieldJournalIssue.VOLUME, required=False)
    journalissue_number = forms.CharField(label=FieldJournalIssue.NUMBER, required=False)
    journalissue_publication_date = forms.DateField(label=FieldJournalIssue.PUBLICATION_DATE, required=False, widget=forms.DateInput(attrs={'class': 'datepicker'}), input_formats=['%d.%m.%Y'])
    journalissue_pages = forms.CharField(label=FieldJournalIssue.PAGES, required=False)
        
    class Meta(AbstractJournalIssueForm.Meta):
        exclude = ('journalissue_title_text', 'journalissue_title_slug', 'journalissue_date_add', 'journalissue_date_edit', 'journalissue_added_by', 'journalissue_modified_by', 'journalissue_authorizations', 'journalissue_is_promoted')

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

    
class ConfirmJournalIssueForm(JournalIssueForm, BaseConfirmModelForm):
    pass



class JournalIssueFileForm(forms.ModelForm):
    file = forms.FileField(label=FieldJournalIssueFile.FILE, widget=FileWidget())
    copyright = forms.CharField(label=FieldJournalIssueFile.COPYRIGHT, widget=Textarea(attrs={'style' : 'height : auto', 'rows': 2}), required=False)

    class Meta:
        model = JournalIssueFile
        exclude = ('book',)


class JournalIssueFileInline(InlineFormSet):
    model = JournalIssueFile
    form_class = JournalIssueFileForm
    extra = 1

        
class JournalIssueLinkForm(forms.ModelForm):
    link = forms.URLField(label=FieldJournalIssueLink.LINK)

    class Meta:
        model = JournalIssueLink
        exclude = ('book',)


class JournalIssueLinkInline(InlineFormSet):
    model = JournalIssueLink
    form_class = JournalIssueLinkForm
    extra = 1
    

class JournalIssueContentContributionAdminForm(forms.ModelForm):
    
    class Meta:
        model = JournalIssueContentContribution
        widgets = {
            'person': autocomplete.ModelSelect2(url='person-autocomplete'),
            'role': autocomplete.Select2(attrs={'class': 'select2'}),
            }
        exclude = ('book',)


class JournalIssueContentContributionForm(forms.ModelForm):
    
    class Meta:
        model = JournalIssueContentContribution
        widgets = {
            'person': AddAnotherWidgetWrapper(autocomplete.ModelSelect2(url='person-autocomplete'), reverse_lazy('person_create'),),
            'role': autocomplete.Select2(attrs={'class': 'select2'}),
            }
        exclude = ('book',)


class JournalIssueContentContributionInline(InlineFormSet):
    model = JournalIssueContentContribution
    form_class = JournalIssueContentContributionForm
    extra = 1

