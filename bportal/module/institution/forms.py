# -*- coding: utf-8 -*-
from ckeditor.widgets import CKEditorWidget
from dal import autocomplete
from django import forms

from bportal.module.common.fields import FieldBaseConfirm
from bportal.module.common.forms import NoHistoryBooleanField

from .fields import FieldInstitution
from .messages import MessageInstitution
from .models import InstitutionType, Institution


class InstitutionTypeAdminForm(forms.ModelForm):
    class Meta:
        model = InstitutionType
        fields = ('__all__')
        

class InstitutionAdminForm(forms.ModelForm):
    institution_description = forms.CharField(label=FieldInstitution.DESCRIPTION, required=False, widget=CKEditorWidget(config_name='leads'))
    force = NoHistoryBooleanField(label=FieldBaseConfirm.FORCE, required=False, initial=False, widget=forms.widgets.HiddenInput())
    
    class Meta:
        model = Institution
        fields = ('__all__')
        widgets = {
            'institution_type': autocomplete.ModelSelect2(url='institutiontype-autocomplete'),
            'institution_parent': autocomplete.ModelSelect2(url='institution-autocomplete'),
            'institution_city': autocomplete.ModelSelect2(url='city-autocomplete'),
            }
        exclude = ('institution_slug',)               


class InstitutionConfirmAdminForm(InstitutionAdminForm):
    
    def clean(self):
        cleaned_data = super(InstitutionConfirmAdminForm, self).clean()
        force = cleaned_data['force']
        if force:
            return cleaned_data
        dup_list = []
        if 'institution_shortname' in cleaned_data:        
            institution_shortname = cleaned_data['institution_shortname']
            dup_list = Institution.objects.filter(institution_shortname=institution_shortname)
            if dup_list:
                self.fields['force'].widget = forms.widgets.CheckboxInput()
                self.fields['force'].required = True
                self.fields['force'].initial = False
                raise forms.ValidationError(MessageInstitution.DUPLICATE_SHORTNAME)
        if not dup_list and 'institution_fullname' in cleaned_data:        
            institution_fullname = cleaned_data['institution_fullname']
            dup_list = Institution.objects.filter(institution_fullname=institution_fullname)
            if dup_list:
                self.fields['force'].widget = forms.widgets.CheckboxInput()
                self.fields['force'].required = True
                self.fields['force'].initial = False
                raise forms.ValidationError(MessageInstitution.DUPLICATE_FULLNAME)
        return cleaned_data
    
    class Meta(InstitutionAdminForm.Meta):
        pass
    

        
