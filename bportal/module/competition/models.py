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
from bportal.module.common.models import TargetGroup, RelatedObject
from bportal.module.event.models import Event
from bportal.module.institution.models import Institution
from bportal.module.person.models import Person, PersonContributionRole
from bportal.settings import BPORTAL_BASE_URL

from .fields import FieldCompetition, FieldCompetitionFile, FieldCompetitionLink, FieldCompetitionContentContribution, FieldCompetitionModification, FieldCompetitionAuthorized
from .messages import MessageCompetition


class TaggedCompetition(TaggedItemBase):
    content_object = models.ForeignKey('Competition')
    
    def __unicode__(self):
        return u'%s' % (self.tag)
    
    def __str__(self):
        return '%s' % (self.tag)

    
@reversion.register(exclude=['competition_is_promoted'], follow=['competition_files', 'competition_links', 'competition_content_contributors'])
class Competition(ModelMeta, models.Model):
    
    def image_file(self, filename):
        currDate = date.today()
        year = str(currDate.year)
        month = str(currDate.month)
        url = "competitions/images/%s/%s/%s" % (year, month, filename)
        return url
        
    competition_id = models.AutoField(primary_key=True)
    competition_title = models.TextField(FieldCompetition.TITLE)
    competition_title_text = models.TextField(FieldCompetition.TITLE)
    competition_title_slug = models.SlugField(unique=False, max_length=128)     
    competition_lead = models.TextField(FieldCompetition.LEAD, null=True, blank=False)
    competition_image = models.ImageField(FieldCompetition.IMAGE, upload_to=image_file, null=True, blank=True)
    competition_image_thumbnail = ImageSpecField(source='competition_image', format='JPEG', options={'quality': 60})
    competition_image_copyright = models.TextField(FieldCompetition.IMAGE_COPYRIGHT, null=True, blank=True)
    competition_image_caption = models.CharField(FieldCompetition.IMAGE_CAPTION, max_length=1024, null=True, blank=True)
    competition_deadline_date = models.DateField(FieldCompetition.DEADLINE_DATE, null=True, blank=True)
    competition_targets = models.ManyToManyField(TargetGroup, verbose_name=FieldCompetition.TARGETS, blank=True, related_name='target_group_competitions+')
    competition_description = models.TextField(FieldCompetition.DESCRIPTION, null=False, blank=False)
    competition_institutions = models.ManyToManyField(Institution, verbose_name=FieldCompetition.INSTITUTIONS, blank=False, related_name='institution_competitions')
    competition_city = models.ForeignKey(City, verbose_name=FieldCompetition.CITY, null=True, blank=True)
    competition_date_add = models.DateTimeField(FieldCompetition.DATE_ADD, default=timezone.now)
    competition_date_edit = models.DateTimeField(FieldCompetition.DATE_EDIT, default=timezone.now)
    competition_keywords = TaggableManager(verbose_name=FieldCompetition.KEYWORDS, through=TaggedCompetition)
    competition_connected_events = models.ManyToManyField(Event, verbose_name=FieldCompetition.CONNECTED_EVENTS, blank=True, related_name='event_connected_competitions')    
    competition_added_by = models.ForeignKey(User, verbose_name=FieldCompetition.ADDED_BY, null=True, blank=True, related_name='user_added_competitions')
    competition_modified_by = models.ForeignKey(User, verbose_name=FieldCompetition.MODIFIED_BY, null=True, blank=True, related_name='user_modified_competitions')
    competition_is_accepted = models.BooleanField(FieldCompetition.IS_ACCEPTED, default=False)
    competition_is_promoted = models.BooleanField(FieldCompetition.IS_PROMOTED, default=False)
    competition_authorizations = models.ManyToManyField(Institution, through='CompetitionAuthorized', through_fields=('competition', 'authorized'), blank=True, related_name='authorization_competitions+')
        
    curr_page = None
    per_page = None
    filter = None
    related_objects = None
    similar_competitions = None 

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
        return self.competition_title_text
        
    def get_meta_description(self):
        if self.competition_lead:
            return strip_tags(self.competition_lead)

    def get_meta_image(self):
        if self.competition_image:
            return self.build_absolute_uri(self.competition_image.url)
       
    def competition_title_safe(self):
        return mark_safe(self.competition_title)
        
    @property
    def competition_related_objects(self):
        if self.related_objects is None:
            self.related_objects = list()
            for e in self.competition_connected_events.all().order_by('event_date_add'):
                r = RelatedObject(e.event_name, e.event_lead, e.event_poster, e.event_date_add, 'event',
                                  e.get_absolute_url())
                self.related_objects.append(r)
            for p in self.competition_connected_projects.all().order_by('project_date_add'):
                r = RelatedObject(p.project_title, p.project_lead, p.project_image, p.project_date_add, 'project',
                                  p.get_absolute_url())
                self.related_objects.append(r)
        
            self.related_objects.sort(key=lambda ro : ro.date_add, reverse=True)
        
        return self.related_objects

    @property
    def competition_similar_competitions(self):
        if self.similar_competitions is None:
            self.similar_competitions = list()
            more_like_this_competitions = SearchQuerySet().models(Competition).more_like_this(self)
            i = 0;
            for competition in more_like_this_competitions:
                if competition.object is None:
                    continue
                c = RelatedObject(competition.object.competition_title, competition.object.competition_lead, competition.object.competition_image,
                                  competition.object.competition_date_add, None, competition.object.get_absolute_url())
                self.similar_competitions.append(c)
                i = i + 1
                if i >= MAX_NUMBER_OF_SIMILAR_ENTITIES:
                    break
            
        return self.similar_competitions   

    def __unicode__(self):
        return u'%s' % (self.competition_title_text)
     
    def __str__(self):
        return self.competition_title_text
     
    def clean(self):
        can_add = True
        if self.competition_is_promoted:
            qrs = Competition.objects.filter(competition_is_promoted=True).exclude(competition_id=self.competition_id)
            can_add = (qrs.count() < MAX_NUMBER_OF_PROMOTED_ENTITIES);
        if not can_add:
            raise ValidationError(MessageCompetition.TO_MANY_PROMOTED)
        models.Model.clean(self)
    
    def get_absolute_url(self):
        return "/" + BPORTAL_BASE_URL + "competitions/%s,%d/details" % (self.competition_title_slug, self.competition_id)
             
    class Meta:
        ordering = ('competition_title_text',)
        verbose_name = FieldCompetition.VERBOSE_NAME
        verbose_name_plural = FieldCompetition.VERBOSE_NAME_PLURAL


@reversion.register
class CompetitionFile(models.Model):

    def competition_files(self, filename):
        currDate = date.today()
        year = str(currDate.year)
        month = str(currDate.month)
        url = "competitions/files/%s/%s/%s" % (year, month, filename)
        return url
    
    competition = models.ForeignKey(Competition, verbose_name=FieldCompetitionFile.COMPETITION, related_name='competition_files')
    file = models.FileField(FieldCompetitionFile.FILE, upload_to=competition_files)
    copyright = models.TextField(FieldCompetitionFile.COPYRIGHT, null=True, blank=True)
    
    def __unicode__(self):
        return u'%s' % (basename(self.file.name))
    
    def __str__(self):
        return '%s' % (basename(self.file.name))
    
    class Meta(object):
        verbose_name = FieldCompetitionFile.VERBOSE_NAME
        verbose_name_plural = FieldCompetitionFile.VERBOSE_NAME_PLURAL


@reversion.register 
class CompetitionLink(models.Model):
    competition = models.ForeignKey(Competition, verbose_name=FieldCompetitionLink.COMPETITION, related_name='competition_links')
    link = models.URLField(FieldCompetitionLink.LINK, null=True, blank=True)
    
    def __unicode__(self):
        return u'%s' % (self.link)
    
    def __str__(self):
        return '%s' % (self.link)
    
    class Meta(object):
        verbose_name = FieldCompetitionLink.VERBOSE_NAME
        verbose_name_plural = FieldCompetitionLink.VERBOSE_NAME_PLURAL


@reversion.register
class CompetitionContentContribution(models.Model):
    competition = models.ForeignKey(Competition, verbose_name=FieldCompetitionContentContribution.COMPETITION, related_name='competition_content_contributors')
    person = models.ForeignKey(Person, verbose_name=FieldCompetitionContentContribution.PERSON)
    role = models.ForeignKey(PersonContributionRole, verbose_name=FieldCompetitionContentContribution.ROLE)
        
    def __unicode__(self):
        return u'%s %s' % (self.competition.competition_title_text, self.person.person_last_name)
    
    def __str__(self):
        return '%s %s' % (self.competition.competition_title_text, self.person.person_last_name)
    
    class Meta(object):
        unique_together = (('competition', 'person'),)
        verbose_name = FieldCompetitionContentContribution.VERBOSE_NAME
        verbose_name_plural = FieldCompetitionContentContribution.VERBOSE_NAME_PLURAL


class CompetitionAuthorized(models.Model):
    competition = models.ForeignKey(Competition, verbose_name=FieldCompetitionAuthorized.COMPETITION)
    authorized = models.ForeignKey(Institution, verbose_name=FieldCompetitionAuthorized.AUTHORIZED)
        
    def __unicode__(self):
        return u'%s %s' % (self.competition.competition_title_text, self.authorized.institution_shortname)
    
    def __str__(self):
        return '%s %s' % (self.competition.competition_title_text, self.authorized.institution_shortname)
    
    class Meta(object):
        unique_together = (('competition', 'authorized'),)
        verbose_name = FieldCompetitionAuthorized.VERBOSE_NAME
        verbose_name_plural = FieldCompetitionAuthorized.VERBOSE_NAME_PLURAL 


class CompetitionModification(models.Model):
    competition = models.ForeignKey(Competition, verbose_name=FieldCompetitionModification.COMPETITION)
    user = models.ForeignKey(User, verbose_name=FieldCompetitionModification.USER)
    date_time = models.DateTimeField(FieldCompetitionModification.DATE_TIME)
    
    def __unicode__(self):
        return u'%s %s' % (self.competition.competition_title_text, self.user.username)
    
    def __str__(self):
        return '%s %s' % (self.competition.competition_title_text, self.user.username)
    
    class Meta(object):
        verbose_name = FieldCompetitionModification.VERBOSE_NAME
        verbose_name_plural = FieldCompetitionModification.VERBOSE_NAME_PLURAL
                
