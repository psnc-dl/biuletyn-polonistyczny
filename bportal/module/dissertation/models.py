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

from bportal.module.common.constants import MAX_NUMBER_OF_PROMOTED_ENTITIES, MAX_NUMBER_OF_SIMILAR_ENTITIES
from bportal.module.common.models import ResearchDiscipline, RelatedObject
from bportal.module.event.models import Event
from bportal.module.institution.models import Institution
from bportal.module.person.models import Person, PersonContributionRole
from bportal.settings import BPORTAL_BASE_URL

from .fields import FieldDissertationType, FieldDissertation, FieldDissertationFile, FieldDissertationLink, FieldDissertationContentContribution, FieldDissertationAuthorized, FieldDissertationModification
from .messages import MessageDissertation


class TaggedDissertation(TaggedItemBase):
    content_object = models.ForeignKey('Dissertation')
    
    def __unicode__(self):
        return u'%s' % (self.tag)
    
    def __str__(self):
        return '%s' % (self.tag)

      
@reversion.register(exclude=['dissertation_is_promoted'], follow=['dissertation_files', 'dissertation_links', 'dissertation_content_contributors'])
class Dissertation(ModelMeta, models.Model):

    def image_file(self, filename):
        currDate = date.today()
        year = str(currDate.year)
        month = str(currDate.month)
        url = "dissertations/images/%s/%s/%s" % (year, month, filename)
        return url
    
    def diss_file(self, filename):
        currDate = date.today()
        year = str(currDate.year)
        month = str(currDate.month)
        url = "dissertations/files/%s/%s/%s" % (year, month, filename)
        return url
    
    DISSERTATION_TYPE_DOC = 'DOC'
    DISSERTATION_TYPE_HAB = 'HAB'
    DISSERTATION_TYPES = (
        (DISSERTATION_TYPE_DOC, FieldDissertationType.DOC_NAME),
        (DISSERTATION_TYPE_HAB, FieldDissertationType.HAB_NAME),
    )
    
    dissertation_id = models.AutoField(primary_key=True)
    dissertation_title = models.TextField(FieldDissertation.TITLE)
    dissertation_title_text = models.TextField(FieldDissertation.TITLE)
    dissertation_title_slug = models.SlugField(unique=False, max_length=128)
    dissertation_lead = models.TextField(FieldDissertation.LEAD, null=True, blank=False)      
    dissertation_date_start = models.DateField(FieldDissertation.DATE_START, null=True, blank=True)
    dissertation_date_end = models.DateField(FieldDissertation.DATE_END, null=True, blank=True)
    dissertation_disciplines = models.ManyToManyField(ResearchDiscipline, verbose_name=FieldDissertation.DISCIPLINES, blank=True, related_name='discipline_dissertations+')
    dissertation_type = models.CharField(FieldDissertation.TYPE, max_length=3, choices=DISSERTATION_TYPES)
    dissertation_image = models.ImageField(FieldDissertation.IMAGE, upload_to=image_file, null=True, blank=True)
    dissertation_image_thumbnail = ImageSpecField(source='dissertation_image', format='JPEG', options={'quality': 60})
    dissertation_image_copyright = models.TextField(FieldDissertation.IMAGE_COPYRIGHT, null=True, blank=True)
    dissertation_image_caption = models.CharField(FieldDissertation.IMAGE_CAPTION, max_length=1024, null=True, blank=True)
    dissertation_supervisors = models.ManyToManyField(Person, verbose_name=FieldDissertation.SUPERVISORS, blank=True, related_name='person_supervised_dissertations')
    dissertation_reviewers = models.ManyToManyField(Person, verbose_name=FieldDissertation.REVIEWERS, blank=True, related_name='person_reviewed_dissertations')
    dissertation_institution = models.ForeignKey(Institution, verbose_name=FieldDissertation.INSTITUTION, null=True, blank=False, related_name='institution_dissertations')
    dissertation_author = models.ForeignKey(Person, verbose_name=FieldDissertation.AUTHOR, null=True, blank=False, related_name='person_dissertations') 
    dissertation_description = models.TextField(FieldDissertation.DESCRIPTION, null=False, blank=False)
    dissertation_file = models.FileField(FieldDissertation.FILE, upload_to=diss_file, null=True, blank=True)
    dissertation_city = models.ForeignKey(City, verbose_name=FieldDissertation.CITY, null=True, blank=True)
    dissertation_date_add = models.DateTimeField(FieldDissertation.DATE_ADD, default=timezone.now)
    dissertation_date_edit = models.DateTimeField(FieldDissertation.DATE_EDIT, default=timezone.now)
    dissertation_keywords = TaggableManager(verbose_name=FieldDissertation.KEYWORDS, through=TaggedDissertation)
    dissertation_connected_events = models.ManyToManyField(Event, verbose_name=FieldDissertation.CONNECTED_EVENTS, blank=True, related_name='event_connected_dissertations')    
    dissertation_added_by = models.ForeignKey(User, verbose_name=FieldDissertation.ADDED_BY, null=True, blank=True, related_name='user_added_dissertations')
    dissertation_modified_by = models.ForeignKey(User, verbose_name=FieldDissertation.MODIFIED_BY, null=True, blank=True, related_name='user_modified_dissertations')
    dissertation_is_accepted = models.BooleanField(FieldDissertation.IS_ACCEPTED, default=False)
    dissertation_is_promoted = models.BooleanField(FieldDissertation.IS_PROMOTED, default=False)
    dissertation_opi_id = models.IntegerField(FieldDissertation.OPI_ID, null=True, blank=True)
    dissertation_authorizations = models.ManyToManyField(Institution, through='DissertationAuthorized', through_fields=('dissertation', 'authorized'), blank=True, related_name='authorization_dissertations+')
        
    curr_page = None
    per_page = None
    filter = None
    related_objects = None
    similar_dissertations = None       
    
    #import
    is_imported = False
    
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
        return self.dissertation_title_text
        
    def get_meta_description(self):
        if self.dissertation_lead:
            return strip_tags(self.dissertation_lead)

    def get_meta_image(self):
        if self.dissertation_image:
            return self.build_absolute_uri(self.dissertation_image.url)
        
    def dissertation_title_safe(self):
        return mark_safe(self.dissertation_title)
    
    @property
    def dissertation_related_objects(self):
        if self.related_objects is None:
            self.related_objects = list()
            for e in self.dissertation_connected_events.all().order_by('event_date_add'):
                r = RelatedObject(e.event_name, e.event_lead, e.event_poster, e.event_date_add, 'event',
                                  e.get_absolute_url())
                self.related_objects.append(r)
            for p in self.dissertation_connected_projects.all().order_by('project_date_add'):
                r = RelatedObject(p.project_title, p.project_lead, p.project_image, p.project_date_add, 'project',
                                  p.get_absolute_url())
                self.related_objects.append(r)
        
            self.related_objects.sort(key=lambda ro : ro.date_add, reverse=True)
        
        return self.related_objects

    @property
    def dissertation_similar_dissertations(self):
        if self.similar_dissertations is None:
            self.similar_dissertations = list()
            more_like_this_dissertations = SearchQuerySet().models(Dissertation).more_like_this(self)
            i = 0;
            for dissertation in more_like_this_dissertations:
                if dissertation.object is None:
                    continue
                d = RelatedObject(dissertation.object.dissertation_title, dissertation.object.dissertation_lead, dissertation.object.dissertation_image,
                                  dissertation.object.dissertation_date_add, None, dissertation.object.get_absolute_url())
                self.similar_dissertations.append(d)
                i = i + 1
                if i >= MAX_NUMBER_OF_SIMILAR_ENTITIES:
                    break
            
        return self.similar_dissertations     

    def __unicode__(self):
        return u'%s' % (self.dissertation_title_text)
     
    def __str__(self):
        if self.dissertation_title_text is not None:
            return self.dissertation_title_text
        else:
            return ''
     
    def clean(self):
        can_add = True
        if self.dissertation_is_promoted:
            qrs = Dissertation.objects.filter(dissertation_is_promoted=True).exclude(dissertation_id=self.dissertation_id)
            can_add = (qrs.count() < MAX_NUMBER_OF_PROMOTED_ENTITIES);
        if not can_add:
            raise ValidationError(MessageDissertation.TO_MANY_PROMOTED)
        models.Model.clean(self)
    
    def get_absolute_url(self):
        return "/" + BPORTAL_BASE_URL + "dissertations/%s,%d/details" % (self.dissertation_title_slug, self.dissertation_id)
        
    def dissertation_file_name(self):
        return basename(self.dissertation_file.file.name)
        
    class Meta:
        ordering = ('dissertation_title_text',)
        verbose_name = FieldDissertation.VERBOSE_NAME
        verbose_name_plural = FieldDissertation.VERBOSE_NAME_PLURAL


@reversion.register
class DissertationFile(models.Model):

    def dissertation_files(self, filename):
        currDate = date.today()
        year = str(currDate.year)
        month = str(currDate.month)
        url = "dissertations/files/%s/%s/%s" % (year, month, filename)
        return url
    
    dissertation = models.ForeignKey(Dissertation, verbose_name=FieldDissertationFile.DISSERTATION, related_name='dissertation_files')
    file = models.FileField(FieldDissertationFile.FILE, upload_to=dissertation_files)
    copyright = models.TextField(FieldDissertationFile.COPYRIGHT, null=True, blank=True)
    
    def __unicode__(self):
        return u'%s' % (basename(self.file.name))
    
    def __str__(self):
        return '%s' % (basename(self.file.name))
    
    class Meta(object):
        verbose_name = FieldDissertationFile.VERBOSE_NAME
        verbose_name_plural = FieldDissertationFile.VERBOSE_NAME_PLURAL


@reversion.register 
class DissertationLink(models.Model):
    dissertation = models.ForeignKey(Dissertation, verbose_name=FieldDissertationLink.DISSERTATION, related_name='dissertation_links')
    link = models.URLField(FieldDissertationLink.LINK, null=True, blank=True)
    
    def __unicode__(self):
        return u'%s' % (self.link)
    
    def __str__(self):
        return '%s' % (self.link)
    
    class Meta(object):
        verbose_name = FieldDissertationLink.VERBOSE_NAME
        verbose_name_plural = FieldDissertationLink.VERBOSE_NAME_PLURAL
        

@reversion.register
class DissertationContentContribution(models.Model):
    dissertation = models.ForeignKey(Dissertation, verbose_name=FieldDissertationContentContribution.DISSERTATION, related_name='dissertation_content_contributors')
    person = models.ForeignKey(Person, verbose_name=FieldDissertationContentContribution.PERSON)
    role = models.ForeignKey(PersonContributionRole, verbose_name=FieldDissertationContentContribution.ROLE)
        
    def __unicode__(self):
        return u'%s %s' % (self.dissertation.dissertation_title_text, self.person.person_last_name)
    
    def __str__(self):
        return '%s %s' % (self.dissertation.dissertation_title_text, self.person.person_last_name)
    
    class Meta(object):
        unique_together = (('dissertation', 'person'),)
        verbose_name = FieldDissertationContentContribution.VERBOSE_NAME
        verbose_name_plural = FieldDissertationContentContribution.VERBOSE_NAME_PLURAL

        
class DissertationAuthorized(models.Model):
    dissertation = models.ForeignKey(Dissertation, verbose_name=FieldDissertationAuthorized.DISSERTATION)
    authorized = models.ForeignKey(Institution, verbose_name=FieldDissertationAuthorized.AUTHORIZED)
        
    def __unicode__(self):
        return u'%s %s' % (self.dissertation.dissertation_title_text, self.authorized.institution_shortname)
    
    def __str__(self):
        return '%s %s' % (self.dissertation.dissertation_title_text, self.authorized.institution_shortname)
    
    class Meta(object):
        unique_together = (('dissertation', 'authorized'),)
        verbose_name = FieldDissertationAuthorized.VERBOSE_NAME
        verbose_name_plural = FieldDissertationAuthorized.VERBOSE_NAME_PLURAL 
        

class DissertationModification(models.Model):
    dissertation = models.ForeignKey(Dissertation, verbose_name=FieldDissertationModification.DISSERTATION)
    user = models.ForeignKey(User, verbose_name=FieldDissertationModification.USER)
    date_time = models.DateTimeField(FieldDissertationModification.DATE_TIME)
    
    def __unicode__(self):
        return u'%s %s' % (self.dissertation.dissertation_title_text, self.user.username)
    
    def __str__(self):
        return '%s %s' % (self.dissertation.dissertation_title_text, self.user.username)
    
    class Meta(object):
        verbose_name = FieldDissertationModification.VERBOSE_NAME
        verbose_name_plural = FieldDissertationModification.VERBOSE_NAME_PLURAL
        
        
