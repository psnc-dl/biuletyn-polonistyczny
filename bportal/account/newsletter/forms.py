# -*- coding: utf-8 -*-
from ckeditor.widgets import CKEditorWidget
from dal import autocomplete
from django import forms

from bportal.account.newsletter.fields import FieldNewsletterCustomContent
from bportal.account.newsletter.models import NewsletterCustomContent

from .models import NewsletterConfig


class NewsletterConfigForm(forms.ModelForm):
     
    class Meta:
        model = NewsletterConfig
        widgets = {
            'event_categories': autocomplete.ModelSelect2Multiple(url='eventcategory-autocomplete'),
            'new_categories': autocomplete.ModelSelect2Multiple(url='newcategory-autocomplete'),
            'period': autocomplete.Select2(attrs={'class': 'select2', 'data-minimum-results-for-search': '-1'}),
        }
          
        exclude = ['user', 'last_sent', 'UUID']
        
        
class NewsletterConfigAdminForm(forms.ModelForm):
    class Meta:
        model = NewsletterConfig
        exclude = ['user', 'UUID']

class NewsletterCustomContentAdminForm(forms.ModelForm):
    title = forms.CharField(label=FieldNewsletterCustomContent.TITLE, widget=CKEditorWidget(config_name='titles'), required=False)
    message = forms.CharField(label=FieldNewsletterCustomContent.MESSAGE, widget=CKEditorWidget(config_name='leads'))

    class Meta:
        model = NewsletterCustomContent
        fields = ('__all__')