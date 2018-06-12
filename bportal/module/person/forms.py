# -*- coding: utf-8 -*-
from ckeditor.widgets import CKEditorWidget
from dal import autocomplete
from django import forms
from extra_views.advanced import InlineFormSet

from bportal.account.profile.widgets import UserPhotoWidget
from bportal.module.common.fields import FieldBaseConfirm
from bportal.module.common.forms import NoHistoryBooleanField, BaseConfirmModelForm

from .fields import FieldPerson
from .messages import MessagePerson
from .models import Person, PersonAffiliation


class AbtractPersonForm(forms.ModelForm):
    person_email = forms.EmailField(label=FieldPerson.EMAIL, required=False)
    person_biogram = forms.CharField(label=FieldPerson.BIOGRAM, required=False, widget=CKEditorWidget(config_name='leads'))

    class Meta:
        abstract = True        
        model = Person
        fields = ('__all__')
        widgets = {
            'person_title': autocomplete.ModelSelect2(url='scientifictitle-autocomplete'),
            'person_disciplines': autocomplete.ModelSelect2Multiple(url='researchdiscipline-autocomplete'),
            }        
        exclude = ('person_institutions', 'person_slug',)


class PersonAdminForm(AbtractPersonForm):
    force = NoHistoryBooleanField(label=FieldBaseConfirm.FORCE, required=False, initial=False, widget=forms.widgets.HiddenInput())

    class Meta(AbtractPersonForm.Meta):
        pass


class PersonConfirmAdminForm(PersonAdminForm):

    def clean(self):
        cleaned_data = super(PersonConfirmAdminForm, self).clean()
        force = cleaned_data['force']
        if force:
            return cleaned_data
        if 'person_first_name' in cleaned_data and 'person_last_name' in cleaned_data:
            first_name = cleaned_data['person_first_name']
            last_name = cleaned_data['person_last_name']
            dup_list = Person.objects.filter(person_first_name=first_name, person_last_name=last_name)
            if dup_list:
                self.fields['force'].widget = forms.widgets.CheckboxInput()
                self.fields['force'].required = True
                self.fields['force'].initial = False
                raise forms.ValidationError(MessagePerson.DUPLICATE)
        return cleaned_data
    
    class Meta(PersonAdminForm.Meta):
        pass


class PersonForm(AbtractPersonForm):
    person_photo = forms.FileField(label=FieldPerson.PHOTO, widget=UserPhotoWidget(), required=False)    
    
    class Meta(AbtractPersonForm.Meta):
        pass

    class Media:
        # # they are not loaded by autocomplete.ModelSelect2 widget
        # # probably widget media do not work in inlines 
        # # force these media in the form
        css = {
            'all': (
                'autocomplete_light/vendor/select2/dist/css/select2.css',
                'autocomplete_light/select2.css',
            )
        }
        js = (
            'autocomplete_light/jquery.init.js',
            'autocomplete_light/autocomplete.init.js',
            'autocomplete_light/vendor/select2/dist/js/select2.full.js',
            'autocomplete_light/select2.js',
        )


class ConfirmPersonForm(PersonForm, BaseConfirmModelForm):
    pass
        
        
class PersonAffiliationForm(forms.ModelForm):
    
    class Meta:
        model = PersonAffiliation
        widgets = {
              'institution': autocomplete.ModelSelect2(url='institution-autocomplete')
            }
        exclude = ('person',)

        
class PersonAffiliationInline(InlineFormSet):
    model = PersonAffiliation
    form_class = PersonAffiliationForm
    extra = 1
