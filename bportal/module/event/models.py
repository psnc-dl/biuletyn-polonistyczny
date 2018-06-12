# -*- coding: utf-8 -*-
from datetime import date
from os.path import basename

from cities_light.models import City
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from haystack.query import SearchQuerySet
from imagekit.models.fields import ImageSpecField
from meta.models import ModelMeta
import reversion
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase

from bportal.module.common.constants import MAX_NUMBER_OF_PROMOTED_EVENTS, MAX_NUMBER_OF_SIMILAR_ENTITIES
from bportal.module.common.models import TargetGroup, RelatedObject
from bportal.module.institution.models import Institution
from bportal.module.person.models import Person, PersonContributionRole
from bportal.settings import BPORTAL_BASE_URL

from .fields import FieldEvent, FieldEventCategory, FieldEventFile, FieldEventLink, FieldEventContentContribution, FieldEventSummary, FieldEventSummaryFile, FieldEventSummaryPicture, FieldEventSummaryPublication, FieldEventSummaryLink, FieldEventSummaryContentContribution, FieldEventAuthorized, FieldEventModification
from .messages import MessageEvent


class EventCategory(models.Model):
    event_category_id = models.AutoField(primary_key=True)
    event_category_name = models.CharField(FieldEventCategory.NAME, max_length=512)

    # # necessary in serializing events to JSON
    def natural_key(self):
        return (self.event_category_name)

    def __unicode__(self):
        return u'%s' % (self.event_category_name)
    
    def __str__(self):
        return self.event_category_name
           
    class Meta:
        ordering = ('event_category_name',)
        verbose_name = FieldEventCategory.VERBOSE_NAME
        verbose_name_plural = FieldEventCategory.VERBOSE_NAME_PLURAL


class TaggedEvent(TaggedItemBase):
    content_object = models.ForeignKey('Event')
    
    def __unicode__(self):
        return u'%s' % (self.tag)
    
    def __str__(self):
        return '%s' % (self.tag)
    

@reversion.register(exclude=['event_is_promoted'], follow=['event_files', 'event_links', 'event_content_contributors'])      
class Event(ModelMeta, models.Model):
    
    def poster_file(self, filename):
        currDate = date.today()
        year = str(currDate.year)
        month = str(currDate.month)
        url = "events/posters/%s/%s/%s" % (year, month, filename)
        return url 
    
    event_id = models.AutoField(primary_key=True)
    event_name = models.TextField(FieldEvent.NAME)
    event_name_text = models.TextField(FieldEvent.NAME)
    event_name_slug = models.SlugField(unique=False, max_length=128)
    event_lead = models.TextField(FieldEvent.LEAD, null=True, blank=False)    
    event_date_from = models.DateField(FieldEvent.DATE_FROM, null=True, blank=True)
    event_time_from = models.TimeField(FieldEvent.TIME_FROM, null=True, blank=True)
    event_date_to = models.DateField(FieldEvent.DATE_TO, null=True, blank=True)
    event_time_to = models.TimeField(FieldEvent.TIME_TO, null=True, blank=True)    
    event_poster = models.ImageField(FieldEvent.POSTER, upload_to=poster_file, null=True, blank=True)
    event_poster_thumbnail = ImageSpecField(source='event_poster', format='JPEG', options={'quality': 60})
    event_poster_copyright = models.TextField(FieldEvent.POSTER_COPYRIGHT, null=True, blank=True)
    event_poster_caption = models.CharField(FieldEvent.POSTER_CAPTION, max_length=2048, null=True, blank=True)
    event_youtube_movie = models.URLField(FieldEvent.YOUTUBE_MOVIE, null=True, blank=True)
    event_city = models.ForeignKey(City, verbose_name=FieldEvent.CITY, null=True, blank=True)
    event_contributors_date = models.DateField(FieldEvent.CONTRIBUTORS_DATE, null=True, blank=True)
    event_contributors_time = models.TimeField(FieldEvent.CONTRIBUTORS_TIME, null=True, blank=True)
    event_participants_date = models.DateField(FieldEvent.PARTICIPANTS_DATE, null=True, blank=True)
    event_participants_time = models.TimeField(FieldEvent.PARTICIPANTS_TIME, null=True, blank=True)    
    event_institutions = models.ManyToManyField(Institution, verbose_name=FieldEvent.INSTITUTIONS, blank=True, related_name='institution_events')
    event_addres = models.CharField(FieldEvent.ADDRESS, max_length=2500, null=True, blank=True)
    event_description = models.TextField(FieldEvent.DESCRIPTION, null=False, blank=False)
    event_fees = models.CharField(FieldEvent.FEES, max_length=2500, null=True, blank=True)
    event_category = models.ForeignKey(EventCategory, verbose_name=FieldEvent.CATEGORY, null=False, blank=False, related_name='event_category_events')
    event_targets = models.ManyToManyField(TargetGroup, verbose_name=FieldEvent.TARGETS, blank=True, related_name='target_events+')
    event_date_add = models.DateTimeField(FieldEvent.DATE_ADD, default=timezone.now)
    event_date_edit = models.DateTimeField(FieldEvent.DATE_EDIT, default=timezone.now)
    event_keywords = TaggableManager(verbose_name=FieldEvent.KEYWORDS, through=TaggedEvent)
    event_added_by = models.ForeignKey(User, verbose_name=FieldEvent.ADDED_BY, null=True, blank=True, related_name='user_added_events')
    event_modified_by = models.ForeignKey(User, verbose_name=FieldEvent.MODIFIED_BY, null=True, blank=True, related_name='user_modified_events')  
    event_is_accepted = models.BooleanField(FieldEvent.IS_ACCEPTED, default=False)
    event_is_promoted = models.BooleanField(FieldEvent.IS_PROMOTED, default=False)
    event_authorizations = models.ManyToManyField(Institution, through='EventAuthorized', through_fields=('event', 'authorized'), blank=True, related_name='authorization_events+')
    
    is_closest = False
    curr_page = None
    per_page = None
    filter = None
    related_objects = None
    similar_events = None 
    
    _metadata = {
        'use_og': 'True',
        'use_facebook': 'True',
        'use_twitter': 'True',
        'use_googleplus': 'True',
        'og_type': 'article',
        'url': 'get_meta_url',
        'title': 'get_meta_title',
        'description': 'get_meta_description',
        'image': 'get_meta_image',
    }
    
    def get_meta_url(self):
        return self.build_absolute_uri(self.get_absolute_url())
    
    def get_meta_title(self):
        return self.event_name_text
        
    def get_meta_description(self):
        if self.event_lead:
            return strip_tags(self.event_lead)

    def get_meta_image(self):
        if self.event_poster:
            return self.build_absolute_uri(self.event_poster.url)
         
    def event_name_safe(self):
        return mark_safe(self.event_name)     
    
    @property
    def event_related_objects(self):
        if self.related_objects is None:
            self.related_objects = list()
            for p in self.event_connected_projects.all().order_by('project_date_add'):
                r = RelatedObject(p.project_title, p.project_lead, p.project_image, p.project_date_add, 'project',
                                  p.get_absolute_url())
                self.related_objects.append(r)
        
            for c in self.event_connected_competitions.all().order_by('competition_date_add'):
                r = RelatedObject(c.competition_title, c.competition_lead, c.competition_image, c.competition_date_add, 'competition',
                                  c.get_absolute_url())
                self.related_objects.append(r)
        
            for d in self.event_connected_dissertations.all().order_by('dissertation_date_add'):
                r = RelatedObject(d.dissertation_title, d.dissertation_lead, d.dissertation_image, d.dissertation_date_add, 'dissertation',
                                  d.get_absolute_url())
                self.related_objects.append(r)

            self.related_objects.sort(key=lambda ro : ro.date_add, reverse=True)
        
        return self.related_objects

    @property
    def event_similar_events(self):
        if self.similar_events is None:
            self.similar_events = list()
            more_like_this_events = SearchQuerySet().models(Event).more_like_this(self)
            i = 0;
            for event in more_like_this_events:
                if event.object is None:
                    continue
                c = RelatedObject(event.object.event_name, event.object.event_lead, event.object.event_poster,
                                  event.object.event_date_add, None, event.object.get_absolute_url())
                self.similar_events.append(c)
                i = i + 1
                if i >= MAX_NUMBER_OF_SIMILAR_ENTITIES:
                    break
            
        return self.similar_events  

    def __unicode__(self):
        return u'%s' % (self.event_name_text)
    
    def __str__(self):
        return self.event_name_text
               
    def clean(self):
        can_add = True
        if self.event_is_promoted:
            qs = Event.objects.filter(event_is_promoted=True).exclude(event_id=self.event_id)
            can_add = (qs.count() < MAX_NUMBER_OF_PROMOTED_EVENTS);
        if not can_add:
            raise ValidationError(MessageEvent.TO_MANY_PROMOTED)
        models.Model.clean(self)
    
    def get_absolute_url(self):
        return "/" + BPORTAL_BASE_URL + "events/%s,%d/details" % (self.event_name_slug, self.event_id)
        
    class Meta:
        ordering = ('event_date_from',)
        verbose_name = FieldEvent.VERBOSE_NAME
        verbose_name_plural = FieldEvent.VERBOSE_NAME_PLURAL


@reversion.register     
class EventFile(models.Model):

    def event_files(self, filename):
        currDate = date.today()
        year = str(currDate.year)
        month = str(currDate.month)
        url = "events/files/%s/%s/%s" % (year, month, filename)
        return url
    
    event = models.ForeignKey(Event, verbose_name=FieldEventFile.EVENT, related_name='event_files')
    file = models.FileField(FieldEventFile.FILE, upload_to=event_files)
    copyright = models.TextField(FieldEventFile.COPYRIGHT, null=True, blank=True)
    
    def __unicode__(self):
        return u'%s' % (basename(self.file.name))
    
    def __str__(self):
        return '%s' % (basename(self.file.name))
    
    class Meta(object):
        verbose_name = FieldEventFile.VERBOSE_NAME
        verbose_name_plural = FieldEventFile.VERBOSE_NAME_PLURAL
        

@reversion.register 
class EventLink(models.Model):
    event = models.ForeignKey(Event, verbose_name=FieldEventLink.EVENT, related_name='event_links')
    link = models.URLField(FieldEventLink.LINK, null=True, blank=True)
    
    def __unicode__(self):
        return u'%s' % (self.link)
    
    def __str__(self):
        return '%s' % (self.link)
    
    class Meta(object):
        verbose_name = FieldEventLink.VERBOSE_NAME
        verbose_name_plural = FieldEventLink.VERBOSE_NAME_PLURAL


@reversion.register
class EventContentContribution(models.Model):
    event = models.ForeignKey(Event, verbose_name=FieldEventContentContribution.EVENT, related_name='event_content_contributors')
    person = models.ForeignKey(Person, verbose_name=FieldEventContentContribution.PERSON)
    role = models.ForeignKey(PersonContributionRole, verbose_name=FieldEventContentContribution.ROLE)
        
    def __unicode__(self):
        return u'%s %s' % (self.event.event_name_text, self.person.person_last_name)
    
    def __str__(self):
        return '%s %s' % (self.event.event_name_text, self.person.person_last_name)
    
    class Meta(object):
        unique_together = (('event', 'person'),)
        verbose_name = FieldEventContentContribution.VERBOSE_NAME
        verbose_name_plural = FieldEventContentContribution.VERBOSE_NAME_PLURAL


@reversion.register(exclude=['event_summary_event'], follow=['event_summary_files', 'event_summary_links', 'event_summary_pictures', 'event_summary_publications', 'event_summary_content_contributors'])   
class EventSummary(ModelMeta, models.Model):
    event_summary_id = models.AutoField(primary_key=True)
    event_summary_lead = models.TextField(FieldEventSummary.LEAD, null=True, blank=False)        
    event_summary_description = models.TextField(FieldEventSummary.DESCRIPTION)
    event_summary_date_add = models.DateTimeField(FieldEventSummary.DATE_ADD, null=True)
    event_summary_added_by = models.ForeignKey(User, verbose_name=FieldEventSummary.ADDED_BY, null=True, blank=True, related_name='user_added_event_summaries')    
    event_summary_event = models.OneToOneField(Event, verbose_name=FieldEventSummary.EVENT, null=False, blank=False, related_name='event_summary')

    _metadata = {
        'use_og': 'True',
        'use_facebook': 'True',
        'use_twitter': 'True',
        'use_googleplus': 'True',        
        'og_type': 'article',
        'url': 'get_meta_url',
        'title': 'get_meta_title',
        'description': 'get_meta_description',
        'image': 'get_meta_image',
    }
    
    def get_meta_url(self):
        return self.build_absolute_uri(self.get_absolute_url())
    
    def get_meta_title(self):
        return self.event_summary_event.event_name_text
        
    def get_meta_description(self):
        if self.event_summary_lead:
            return strip_tags(self.event_summary_lead)

    def get_meta_image(self):
        if self.event_summary_pictures.all():
            return self.build_absolute_uri(self.event_summary_pictures.all()[0].file.url)

    def __unicode__(self):
        return u'%s' % (self.event_summary_lead[:128])
    
    def __str__(self):
        return self.event_summary_lead[:128]  
    
    def get_absolute_url(self):
        return "/" + BPORTAL_BASE_URL + "events/summary/%s,%d/details" % (self.event_summary_event.event_name_slug, self.event_summary_event.event_id)
    
    class Meta:
        verbose_name = FieldEventSummary.VERBOSE_NAME
        verbose_name_plural = FieldEventSummary.VERBOSE_NAME_PLURAL
        
        
@reversion.register        
class EventSummaryFile(models.Model):
    
    def summary_files(self, filename):
        currDate = date.today()
        year = str(currDate.year)
        month = str(currDate.month)
        url = "events/summary_files/%s/%s/%s" % (year, month, filename)
        return url
    
    event_summary = models.ForeignKey(EventSummary, verbose_name=FieldEventSummaryFile.EVENT_SUMMARY, related_name='event_summary_files')
    file = models.FileField(FieldEventSummaryFile.FILE, upload_to=summary_files)
    copyright = models.TextField(FieldEventSummaryFile.COPYRIGHT, null=True, blank=True)
    
    def __unicode__(self):
        return u'%s' % (basename(self.file.name))
    
    def __str__(self):
        return '%s' % (basename(self.file.name))
        
    class Meta:
        verbose_name = FieldEventSummaryFile.VERBOSE_NAME
        verbose_name_plural = FieldEventSummaryFile.VERBOSE_NAME_PLURAL


@reversion.register
class EventSummaryLink(models.Model):
    event_summary = models.ForeignKey(EventSummary, verbose_name=FieldEventSummaryLink.EVENT_SUMMARY, related_name='event_summary_links')
    link = models.URLField(FieldEventSummaryLink.LINK, null=True, blank=True)
    
    def __unicode__(self):
        return u'%s' % (self.link)
    
    def __str__(self):
        return '%s' % (self.link)
    
    class Meta(object):
        verbose_name = FieldEventSummaryLink.VERBOSE_NAME
        verbose_name_plural = FieldEventSummaryLink.VERBOSE_NAME_PLURAL
        

@reversion.register        
class EventSummaryPicture(models.Model):
    
    def summary_pictures(self, filename):
        currDate = date.today()
        year = str(currDate.year)
        month = str(currDate.month)
        url = "events/summary_pictures/%s/%s/%s" % (year, month, filename)
        return url
    
    event_summary = models.ForeignKey(EventSummary, verbose_name=FieldEventSummaryPicture.EVENT_SUMMARY, related_name='event_summary_pictures')
    file = models.FileField(FieldEventSummaryPicture.FILE, upload_to=summary_pictures)
    copyright = models.TextField(FieldEventSummaryPicture.COPYRIGHT, null=True, blank=True)
    description = models.CharField(FieldEventSummaryPicture.DESCRIPTION, null=True, blank=True, max_length=1024)

    def __unicode__(self):
        return u'%s' % (self.file.name)
    
    def __str__(self):
        return '%s' % (self.file.name)

    class Meta:
        ordering = ['id']
        verbose_name = FieldEventSummaryPicture.VERBOSE_NAME
        verbose_name_plural = FieldEventSummaryPicture.VERBOSE_NAME_PLURAL


@reversion.register    
class EventSummaryPublication(models.Model):
    
    def cover_files(self, filename):
        currDate = date.today()
        year = str(currDate.year)
        month = str(currDate.month)
        url = "events/publication_covers/%s/%s/%s" % (year, month, filename)
        return url
    
    def publication_files(self, filename):
        currDate = date.today()
        year = str(currDate.year)
        month = str(currDate.month)
        url = "events/publication_files/%s/%s/%s" % (year, month, filename)
        return url
    
    event_publication_id = models.AutoField(primary_key=True)
    event_publication_title = models.CharField(FieldEventSummaryPublication.TITLE, max_length=1024)
    event_publication_editor = models.CharField(FieldEventSummaryPublication.EDITOR, max_length=512)
    event_publication_link = models.URLField(FieldEventSummaryPublication.LINK, null=True, blank=True)
    event_publication_cover = models.ImageField(FieldEventSummaryPublication.COVER, upload_to=cover_files, null=True, blank=True)
    event_publication_file = models.FileField(FieldEventSummaryPublication.FILE, upload_to=publication_files, null=True, blank=True)
    event_publication_summary = models.ForeignKey(EventSummary, verbose_name=FieldEventSummaryPublication.EVENT_SUMMARY, null=False, blank=False, related_name='event_summary_publications')
    
    def __unicode__(self):
        return u'%s' % (self.event_publication_title)
    
    def __str__(self):
        return self.event_publication_title  

    class Meta:
        verbose_name = FieldEventSummaryPublication.VERBOSE_NAME
        verbose_name_plural = FieldEventSummaryPublication.VERBOSE_NAME_PLURAL


@reversion.register 
class EventSummaryContentContribution(models.Model):
    event_summary = models.ForeignKey(EventSummary, verbose_name=FieldEventSummaryContentContribution.EVENT_SUMMARY, related_name='event_summary_content_contributors')
    person = models.ForeignKey(Person, verbose_name=FieldEventSummaryContentContribution.PERSON)
    role = models.ForeignKey(PersonContributionRole, verbose_name=FieldEventSummaryContentContribution.ROLE)
        
    def __unicode__(self):
        return u'%s %s' % (self.event_summary.event_summary_event.event_name_text, self.person.person_last_name)
    
    def __str__(self):
        return '%s %s' % (self.event_summary.event_summary_event.event_name_text, self.person.person_last_name)
    
    class Meta(object):
        unique_together = (('event_summary', 'person'),)
        verbose_name = FieldEventSummaryContentContribution.VERBOSE_NAME
        verbose_name_plural = FieldEventSummaryContentContribution.VERBOSE_NAME_PLURAL
        

class EventAuthorized(models.Model):
    event = models.ForeignKey(Event, verbose_name=FieldEventAuthorized.EVENT)
    authorized = models.ForeignKey(Institution, verbose_name=FieldEventAuthorized.AUTHORIZED)
        
    def __unicode__(self):
        return u'%s %s' % (self.event.event_name_text, self.authorized.institution_shortname)
    
    def __str__(self):
        return '%s %s' % (self.event.event_name_text, self.authorized.institution_shortname)
    
    class Meta(object):
        unique_together = (('event', 'authorized'),)
        verbose_name = FieldEventAuthorized.VERBOSE_NAME
        verbose_name_plural = FieldEventAuthorized.VERBOSE_NAME_PLURAL
        

class EventModification(models.Model):
    event = models.ForeignKey(Event, verbose_name=FieldEventModification.EVENT)
    user = models.ForeignKey(User, verbose_name=FieldEventModification.USER)
    date_time = models.DateTimeField(FieldEventModification.DATE_TIME)
    
    def __unicode__(self):
        return u'%s %s' % (self.event.event_name_text, self.user.username)
    
    def __str__(self):
        return '%s %s' % (self.event.event_name_text, self.user.username)
    
    class Meta(object):
        verbose_name = FieldEventModification.VERBOSE_NAME
        verbose_name_plural = FieldEventModification.VERBOSE_NAME_PLURAL
