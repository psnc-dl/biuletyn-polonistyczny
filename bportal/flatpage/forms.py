# -*- coding: utf-8 -*-
from django import forms
from .fields import FieldFlatPage
from django.contrib.flatpages.models import FlatPage
from ckeditor_uploader.widgets import CKEditorUploadingWidget


class FlatPageForm(forms.ModelForm):
    content = forms.CharField(label=FieldFlatPage.CONTENT, widget=CKEditorUploadingWidget(config_name='flat_pages'))
    
    class Meta:
        model = FlatPage
        fields = ('__all__')

        
        