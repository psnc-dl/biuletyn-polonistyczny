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

from .fields import FieldBook, FieldBookFile, FieldBookLink 
from .messages import MessageBook
from .models import Book, BookFile, BookLink, BookContentContribution


class AbstractBookForm(forms.ModelForm):
    book_title = forms.CharField(label=FieldBook.TITLE, widget=CKEditorWidget(config_name='titles'))
    book_lead = forms.CharField(label=FieldBook.LEAD, widget=CKEditorWidget(config_name='leads'))
    book_image_copyright = forms.CharField(label=FieldBook.IMAGE_COPYRIGHT, widget=Textarea(attrs={'style' : 'height : auto', 'rows': 2}), required=False)
    book_description = forms.CharField(label=FieldBook.DESCRIPTION, widget=CKEditorUploadingWidget())  
    book_table_of_contents = forms.CharField(label=FieldBook.TABLE_OF_CONTENTS, widget=CKEditorWidget(), required=False)
    book_keywords = HistoryTagField(label=FieldBook.KEYWORDS)    
    
    class Meta:
        abstract = True
        model = Book
        fields = ('__all__')
        widgets = {
            'book_category': autocomplete.ModelSelect2(url='publicationcategory-autocomplete'),
            'book_authors': autocomplete.ModelSelect2Multiple(url='person-autocomplete'),
            'book_publisher' : autocomplete.ModelSelect2(url='institution-autocomplete'),
            }
        exclude = ('book_title_text', 'book_title_slug', 'book_date_add', 'book_date_edit', 'book_added_by', 'book_modified_by', 'book_authorizations')
        

class BookAdminForm(AbstractBookForm):
    force = NoHistoryBooleanField(label=FieldBaseConfirm.FORCE, required=False, initial=False, widget=forms.widgets.HiddenInput())
    
    class Meta(AbstractBookForm.Meta):
        pass

        
class BookConfirmAdminForm(BookAdminForm):
        
    def clean(self):
        cleaned_data = super(BookConfirmAdminForm, self).clean()
        force = cleaned_data['force']
        if force is True:
            return cleaned_data
        if 'book_title' in cleaned_data:
            title = cleaned_data['book_title']
            title = remove_unnecessary_tags_from_title(title)
            title = strip_tags(title)             
            dup_list = Book.objects.filter(book_title_text=title)
            if dup_list:
                self.fields['force'].widget = forms.widgets.CheckboxInput()
                self.fields['force'].required = True
                self.fields['force'].initial = False
                raise forms.ValidationError(MessageBook.DUPLICATE)
        return cleaned_data
    
    class Meta(BookAdminForm.Meta):
        pass


class BookForm(AbstractBookForm):
    book_image = forms.ImageField(label=FieldBook.IMAGE, widget=FileWidget(), required=False)
    book_isbn = forms.CharField(label=FieldBook.ISBN, required=False)
    book_publication_date = forms.DateField(label=FieldBook.PUBLICATION_DATE, required=False, widget=forms.DateInput(attrs={'class': 'datepicker'}), input_formats=['%d.%m.%Y'])
    book_pages = forms.CharField(label=FieldBook.PAGES, required=False)
    
    class Meta(AbstractBookForm.Meta):
        exclude = ('book_title_text', 'book_title_slug', 'book_date_add', 'book_date_edit', 'book_added_by', 'book_modified_by', 'book_authorizations', 'book_is_promoted')

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

    
class ConfirmBookForm(BookForm, BaseConfirmModelForm):
    pass



class BookFileForm(forms.ModelForm):
    file = forms.FileField(label=FieldBookFile.FILE, widget=FileWidget())
    copyright = forms.CharField(label=FieldBookFile.COPYRIGHT, widget=Textarea(attrs={'style' : 'height : auto', 'rows': 2}), required=False)

    class Meta:
        model = BookFile
        exclude = ('book',)


class BookFileInline(InlineFormSet):
    model = BookFile
    form_class = BookFileForm
    extra = 1

        
class BookLinkForm(forms.ModelForm):
    link = forms.URLField(label=FieldBookLink.LINK)

    class Meta:
        model = BookLink
        exclude = ('book',)


class BookLinkInline(InlineFormSet):
    model = BookLink
    form_class = BookLinkForm
    extra = 1
    

class BookContentContributionAdminForm(forms.ModelForm):
    
    class Meta:
        model = BookContentContribution
        widgets = {
            'person': autocomplete.ModelSelect2(url='person-autocomplete'),
            'role': autocomplete.Select2(attrs={'class': 'select2'}),
            }
        exclude = ('book',)


class BookContentContributionForm(forms.ModelForm):
    
    class Meta:
        model = BookContentContribution
        widgets = {
            'person': AddAnotherWidgetWrapper(autocomplete.ModelSelect2(url='person-autocomplete'), reverse_lazy('person_create'),),
            'role': autocomplete.Select2(attrs={'class': 'select2'}),
            }
        exclude = ('book',)


class BookContentContributionInline(InlineFormSet):
    model = BookContentContribution
    form_class = BookContentContributionForm
    extra = 1

