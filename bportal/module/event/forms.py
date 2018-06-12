# -*- coding: utf-8 -*-
from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from dal import autocomplete
from django import forms
from django.core.urlresolvers import reverse_lazy
from django.forms.widgets import URLInput, Textarea
from django.utils.html import strip_tags
from django_addanother.widgets import AddAnotherWidgetWrapper
from extra_views.advanced import InlineFormSet

from bportal.module.common.fields import FieldBaseConfirm
from bportal.module.common.forms import NoHistoryBooleanField, BaseConfirmModelForm, HistoryTagField
from bportal.module.common.utils import remove_unnecessary_tags_from_title
from bportal.module.common.widgets import FileWidget
from bportal.module.competition.models import Competition
from bportal.module.dissertation.models import Dissertation
from bportal.module.project.models import Project

from .fields import FieldEvent, FieldEventLink, FieldEventFile, FieldEventSummary, FieldEventSummaryLink, FieldEventSummaryFile, FieldEventSummaryPicture, FieldEventSummaryPublication
from .messages import MessageEvent
from .models import EventCategory, Event, EventFile, EventLink, EventContentContribution, EventSummary, EventSummaryLink, EventSummaryFile, EventSummaryPicture, EventSummaryPublication, EventSummaryContentContribution


class EventCategoryAdminForm(forms.ModelForm):            
    class Meta:
        model = EventCategory
        fields = ('__all__')


class AbstractEventForm(forms.ModelForm):
    event_name = forms.CharField(label=FieldEvent.NAME, widget=CKEditorWidget(config_name='titles'))
    event_lead = forms.CharField(label=FieldEvent.LEAD, widget=CKEditorWidget(config_name='leads'))        
    event_poster_copyright = forms.CharField(label=FieldEvent.POSTER_COPYRIGHT, widget=Textarea(attrs={'style' : 'height : auto', 'rows': 2}), required=False)
    event_description = forms.CharField(label=FieldEvent.DESCRIPTION, widget=CKEditorUploadingWidget())
    event_keywords = HistoryTagField(label=FieldEvent.KEYWORDS)
    event_connected_projects = forms.ModelMultipleChoiceField(label=FieldEvent.CONNECTED_PROJECTS, required=False, queryset=Project.objects.all(),
                                                              widget=autocomplete.ModelSelect2Multiple(url='project-autocomplete'))  # related_name field has to be defined in the form    
    event_connected_dissertations = forms.ModelMultipleChoiceField(label=FieldEvent.CONNECTED_DISSERTATIONS, required=False, queryset=Dissertation.objects.all(),
                                                              widget=autocomplete.ModelSelect2Multiple(url='dissertation-autocomplete'))  # related_name field has to be defined in the form
    event_connected_competitions = forms.ModelMultipleChoiceField(label=FieldEvent.CONNECTED_COMPETITIONS, required=False, queryset=Competition.objects.all(),
                                                              widget=autocomplete.ModelSelect2Multiple(url='competition-autocomplete'))  # related_name field has to be defined in the form
      
    def __init__(self, *args, **kwargs):
        if kwargs.get('instance'):
            initial = kwargs.setdefault('initial', {})
            # the widget for a ModelMultipleChoiceField expects a list of primary key for the selected data
            initial['event_connected_projects'] = [project.project_id for project in kwargs['instance'].event_connected_projects.all()]
            initial['event_connected_dissertations'] = [dissertation.dissertation_id for dissertation in kwargs['instance'].event_connected_dissertations.all()]
            initial['event_connected_competitions'] = [competition.competition_id for competition in kwargs['instance'].event_connected_competitions.all()]            
        super(AbstractEventForm, self).__init__(*args, **kwargs)            
           
    def clean_event_date_to(self):   
        try:
            dateFrom = self.cleaned_data.get('event_date_from', None)
            dateTo = self.cleaned_data.get('event_date_to', None)
        except:
            raise forms.ValidationError(MessageEvent.INCORRECT_DATE)
        if dateFrom is not None and dateTo is not None:
            if dateFrom > dateTo:
                raise forms.ValidationError(MessageEvent.INCORRECT_PERIOD)
        return dateTo
                            
    def _save_m2m(self):
        instance = self.instance
        instance.event_connected_projects.clear()
        instance.event_connected_dissertations.clear()
        instance.event_connected_competitions.clear()
        for project in self.cleaned_data['event_connected_projects']:
            instance.event_connected_projects.add(project)
        for dissertation in self.cleaned_data['event_connected_dissertations']:
            instance.event_connected_dissertations.add(dissertation)
        for competition in self.cleaned_data['event_connected_competitions']:
            instance.event_connected_competitions.add(competition)            
        super(AbstractEventForm, self)._save_m2m()                        
                       
    class Meta:
        abstract = True
        model = Event
        fields = ('__all__')
        widgets = {
            'event_category': autocomplete.ModelSelect2(url='eventcategory-autocomplete'),
            'event_targets': autocomplete.ModelSelect2Multiple(url='targetgroup-autocomplete'),
            'event_institutions': autocomplete.ModelSelect2Multiple(url='institution-autocomplete'),
            'event_city': autocomplete.ModelSelect2(url='city-autocomplete'),
        }
        exclude = ('event_name_text', 'event_name_slug', 'event_date_add', 'event_date_edit', 'event_added_by', 'event_modified_by', 'event_authorizations')


class EventAdminForm(AbstractEventForm):
    force = NoHistoryBooleanField(label=FieldBaseConfirm.FORCE, required=False, initial=False, widget=forms.widgets.HiddenInput())

    class Meta(AbstractEventForm.Meta):
        pass
    

class EventConfirmAdminForm(EventAdminForm):
        
    def clean(self):
        cleaned_data = super(EventConfirmAdminForm, self).clean()
        force = cleaned_data['force']
        if force:
            return cleaned_data
        if 'event_name' in cleaned_data:
            name = cleaned_data['event_name']
            name = remove_unnecessary_tags_from_title(name)
            name = strip_tags(name)   
            dup_list = Event.objects.filter(event_name_text=name)
            if dup_list:
                self.fields['force'].widget = forms.widgets.CheckboxInput()
                self.fields['force'].required = True
                self.fields['force'].initial = False
                raise forms.ValidationError(MessageEvent.DUPLICATE)
        return cleaned_data  
    
    class Meta(EventAdminForm.Meta):
        pass


class EventForm(AbstractEventForm):
    event_poster = forms.ImageField(label=FieldEvent.POSTER, widget=FileWidget(), required=False)
    event_date_from = forms.DateField(label=FieldEvent.DATE_FROM, widget=forms.DateInput(attrs={'class': 'datepicker'}), input_formats=['%d.%m.%Y'])
    event_time_from = forms.TimeField(label=FieldEvent.TIME_FROM, required=False, widget=forms.TimeInput(attrs={'class': 'timepicker'}))
    event_date_to = forms.DateField(label=FieldEvent.DATE_TO, required=False, widget=forms.DateInput(attrs={'class': 'datepicker'}), input_formats=['%d.%m.%Y'])
    event_time_to = forms.TimeField(label=FieldEvent.TIME_TO, required=False, widget=forms.TimeInput(attrs={'class': 'timepicker'}))
    event_contributors_date = forms.DateField(label=FieldEvent.CONTRIBUTORS_DATE, required=False, widget=forms.DateInput(attrs={'class': 'datepicker'}), input_formats=['%d.%m.%Y'])
    event_contributors_time = forms.TimeField(label=FieldEvent.CONTRIBUTORS_TIME, required=False, widget=forms.TimeInput(attrs={'class': 'timepicker'}))
    event_participants_date = forms.DateField(label=FieldEvent.PARTICIPANTS_DATE, required=False, widget=forms.DateInput(attrs={'class': 'datepicker'}), input_formats=['%d.%m.%Y'])
    event_participants_time = forms.TimeField(label=FieldEvent.PARTICIPANTS_TIME, required=False, widget=forms.TimeInput(attrs={'class': 'timepicker'}))
        
    class Meta(AbstractEventForm.Meta):
        exclude = ('event_name_text', 'event_name_slug', 'event_date_add', 'event_date_edit', 'event_added_by', 'event_modified_by', 'event_authorizations', 'event_is_promoted')        
        
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
        
        
class ConfirmEventModelForm(EventForm, BaseConfirmModelForm):
    pass


class EventFileForm(forms.ModelForm):
    file = forms.FileField(label=FieldEventFile.FILE, widget=FileWidget())
    copyright = forms.CharField(label=FieldEventFile.COPYRIGHT, widget=Textarea(attrs={'style' : 'height : auto', 'rows': 2}), required=False)
    
    class Meta:
        model = EventFile
        exclude = ('event',)
        
        
class EventFileInline(InlineFormSet):
    model = EventFile
    form_class = EventFileForm
    extra = 1
    

class EventLinkForm(forms.ModelForm):
    link = forms.URLField(label=FieldEventLink.LINK)
    
    class Meta:
        model = EventLink
        exclude = ('event',)
        
        
class EventLinkInline(InlineFormSet):
    model = EventLink
    form_class = EventLinkForm
    extra = 1


class EventContentContributionAdminForm(forms.ModelForm):
    
    class Meta:
        model = EventContentContribution
        widgets = {
            'person': autocomplete.ModelSelect2(url='person-autocomplete'),
            'role': autocomplete.Select2(attrs={'class': 'select2'}),
            }
        exclude = ('event',)


class EventContentContributionForm(forms.ModelForm):
    
    class Meta:
        model = EventContentContribution
        widgets = {
            'person': AddAnotherWidgetWrapper(autocomplete.ModelSelect2(url='person-autocomplete'), reverse_lazy('person_create'),),
            'role': autocomplete.Select2(attrs={'class': 'select2'}),
            }
        exclude = ('event',)


class EventContentContributionInline(InlineFormSet):
    model = EventContentContribution
    form_class = EventContentContributionForm
    extra = 1


class AbstractEventSummaryForm(forms.ModelForm):
    event_summary_lead = forms.CharField(label=FieldEventSummary.LEAD, widget=CKEditorWidget(config_name='leads'))
    event_summary_description = forms.CharField(label=FieldEvent.DESCRIPTION, widget=CKEditorUploadingWidget()) 

    class Meta:
        abstract = True
        model = EventSummary
        fields = ('__all__')
        exclude = ('event_summary_date_add', 'event_summary_added_by')



class EventSummaryAdminForm(AbstractEventSummaryForm):

    class Meta:
        widgets = {
            'event_summary_event': autocomplete.ModelSelect2(url='event-autocomplete'),
        }


class EventSummaryForm(AbstractEventSummaryForm):
    event_summary_event = forms.CharField(widget=forms.widgets.HiddenInput())
    
    class Media:
        # # they are not loaded by AddAnotherWidgetWrapper widget
        # # probably widget media do not work in inlines 
        # # force these media in the form        
        # # moreover select2 is not loaded since there is no widget that needs it in the basic form
        css = {
            'all': ('autocomplete_light/vendor/select2/dist/css/select2.css',
                    'autocomplete_light/select2.css',
                    'django_addanother/addanother.css', 
                )
        }
        js = (
            'autocomplete_light/jquery.init.js',
            'autocomplete_light/autocomplete.init.js',
            'autocomplete_light/vendor/select2/dist/js/select2.full.js',
            'autocomplete_light/select2.js',
            'django_addanother/django_jquery.js',
            'admin/js/admin/RelatedObjectLookups.js',
        )


class EventSummaryLinkForm(forms.ModelForm):
    link = forms.URLField(label=FieldEventSummaryLink.LINK)
    
    class Meta:
        model = EventSummaryLink
        exclude = ('event_summary',)
                

class EventSummaryLinkInline(InlineFormSet):
    model = EventSummaryLink
    form_class = EventSummaryLinkForm
    extra = 1


class EventSummaryFileForm(forms.ModelForm):
    file = forms.FileField(label=FieldEventSummaryFile.FILE, widget=FileWidget())
    copyright = forms.CharField(label=FieldEventSummaryFile.COPYRIGHT, widget=Textarea(attrs={'style' : 'height : auto', 'rows': 2}), required=False)
    
    class Meta:
        model = EventSummaryFile
        exclude = ('event_summary',)


class EventSummaryFileInline(InlineFormSet):
    model = EventSummaryFile
    form_class = EventSummaryFileForm
    extra = 1


class EventSummaryPictureForm(forms.ModelForm):
    file = forms.ImageField(label=FieldEventSummaryPicture.FILE, widget=FileWidget())
    copyright = forms.CharField(label=FieldEventSummaryPicture.COPYRIGHT, widget=Textarea(attrs={'style' : 'height : auto', 'rows': 2}), required=False)
    
    class Meta:
        model = EventSummaryPicture
        exclude = ('event_summary',)


class EventSummaryPictureInline(InlineFormSet):
    model = EventSummaryPicture
    form_class = EventSummaryPictureForm
    extra = 1

        
class EventSummaryPublicationForm(forms.ModelForm):
    event_publication_link = forms.URLField(label=FieldEventSummaryPublication.LINK, widget=URLInput(), required=False)   
    event_publication_cover = forms.FileField(label=FieldEventSummaryPublication.COVER, widget=FileWidget(), required=False)
    event_publication_file = forms.FileField(label=FieldEventSummaryPublication.FILE, widget=FileWidget(), required=False)

    class Meta:
        model = EventSummaryPublication
        exclude = ('event_publication_summary',)


class EventSummaryPublicationInline(InlineFormSet):
    model = EventSummaryPublication
    form_class = EventSummaryPublicationForm
    extra = 1
    
        
class EventSummaryContentContributionAdminForm(forms.ModelForm):
    
    class Meta:
        model = EventSummaryContentContribution
        widgets = {
            'person': autocomplete.ModelSelect2(url='person-autocomplete'),
            'role': autocomplete.Select2(attrs={'class': 'select2'}),
            }
        exclude = ('event_summary',)


class EventSummaryContentContributionForm(forms.ModelForm):
    
    class Meta:
        model = EventSummaryContentContribution
        widgets = {
            'person': AddAnotherWidgetWrapper(autocomplete.ModelSelect2(url='person-autocomplete'), reverse_lazy('person_create'),),
            'role': autocomplete.Select2(attrs={'class': 'select2'}),
            }
        exclude = ('event_summary',)


class EventSummaryContentContributionInline(InlineFormSet):
    model = EventSummaryContentContribution
    form_class = EventSummaryContentContributionForm
    extra = 1
