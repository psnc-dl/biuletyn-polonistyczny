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
from bportal.module.common.models import RelatedObject
from bportal.module.institution.models import Institution
from bportal.module.person.models import Person, PersonContributionRole
from bportal.settings import BPORTAL_BASE_URL

from .fields import FieldJobOfferDiscipline, FieldJobOfferType, FieldJobOffer, FieldJobOfferFile, FieldJobOfferLink, FieldJobOfferContentContribution, FieldJobOfferAuthorized, FieldJobOfferModification
from .messages import MessageJobOffer


class JobOfferDiscipline(models.Model):
    discipline_id = models.AutoField(primary_key=True)
    discipline_name = models.CharField(FieldJobOfferDiscipline.NAME, max_length=1024)
     
    def __unicode__(self):
        return u'%s' % (self.discipline_name)
    
    def __str__(self):
        return self.discipline_name
    
    class Meta:
        ordering = ('discipline_name',)        
        verbose_name = FieldJobOfferDiscipline.VERBOSE_NAME
        verbose_name_plural = FieldJobOfferDiscipline.VERBOSE_NAME_PLURAL
        

class JobOfferType(models.Model):
    type_id = models.AutoField(primary_key=True)
    type_name = models.CharField(FieldJobOfferType.TYPE_NAME, max_length=1024)
    
    def __unicode__(self):
        return u'%s' % (self.type_name)
    
    def __str__(self):
        return self.type_name
    
    class Meta:
        ordering = ('type_name',)
        verbose_name = FieldJobOfferType.VERBOSE_NAME
        verbose_name_plural = FieldJobOfferType.VERBOSE_NAME_PLURAL


class TaggedJobOffer(TaggedItemBase):
    content_object = models.ForeignKey('JobOffer')
    
    def __unicode__(self):
        return u'%s' % (self.tag)
    
    def __str__(self):
        return '%s' % (self.tag)
    

@reversion.register(exclude=['joboffer_is_promoted'], follow=['joboffer_files', 'joboffer_links', 'joboffer_content_contributors']) 
class JobOffer(ModelMeta, models.Model):
    
    def image_file(self, filename):
        currDate = date.today()
        year = str(currDate.year)
        month = str(currDate.month)
        url = "joboffers/images/%s/%s/%s" % (year, month, filename)
        return url
    
    joboffer_id = models.AutoField(primary_key=True)
    joboffer_position = models.TextField(FieldJobOffer.POSITION)
    joboffer_position_text = models.TextField(FieldJobOffer.POSITION)
    joboffer_position_slug = models.SlugField(unique=False, max_length=128)
    joboffer_lead = models.TextField(FieldJobOffer.LEAD, null=True, blank=False)    
    joboffer_image = models.ImageField(FieldJobOffer.IMAGE, upload_to=image_file, null=True, blank=True)
    joboffer_image_thumbnail = ImageSpecField(source='joboffer_image', format='JPEG', options={'quality': 60})
    joboffer_image_copyright = models.TextField(FieldJobOffer.IMAGE_COPYRIGHT, null=True, blank=True)
    joboffer_image_caption = models.CharField(FieldJobOffer.IMAGE_CAPTION, max_length=1024, null=True, blank=True)
    joboffer_type = models.ForeignKey(JobOfferType, null=True, blank=True, verbose_name=FieldJobOffer.TYPE, related_name='type_joboffers+')
    joboffer_disciplines = models.ManyToManyField(JobOfferDiscipline, verbose_name=FieldJobOffer.DISCIPLINES, related_name='discipline_joboffers+', blank=True)
    joboffer_cities = models.ManyToManyField(City, verbose_name=FieldJobOffer.CITIES, related_name='city_joboffers+', blank=True)
    joboffer_description = models.TextField(FieldJobOffer.DESCRIPTION, null=False, blank=False)
    joboffer_date_start = models.DateField(FieldJobOffer.DATE_START, null=True, blank=True)
    joboffer_date_end = models.DateField(FieldJobOffer.DATE_END, null=True, blank=True)
    joboffer_institution = models.ForeignKey(Institution, null=True, blank=True, verbose_name=FieldJobOffer.INSTITUTION, related_name='institution_joboffers')
    joboffer_keywords = TaggableManager(verbose_name=FieldJobOffer.KEYWORDS, through=TaggedJobOffer)
    joboffer_date_add = models.DateTimeField(FieldJobOffer.DATE_ADD, default=timezone.now)
    joboffer_date_edit = models.DateTimeField(FieldJobOffer.DATE_EDIT, default=timezone.now)
    joboffer_added_by = models.ForeignKey(User, verbose_name=FieldJobOffer.ADDED_BY, null=True, blank=True, related_name='user_added_joboffers')
    joboffer_modified_by = models.ForeignKey(User, verbose_name=FieldJobOffer.MODIFIED_BY, null=True, blank=True, related_name='user_modified_joboffers')
    joboffer_is_promoted = models.BooleanField(FieldJobOffer.IS_PROMOTED, default=False)
    joboffer_is_accepted = models.BooleanField(FieldJobOffer.IS_ACCEPTED, default=False)
    joboffer_authorizations = models.ManyToManyField(Institution, through='JobOfferAuthorized', through_fields=('joboffer', 'authorized'), blank=True, related_name='authorization_joboffers+')
    
    curr_page = None
    per_page = None
    filter = None
    related_objects = None
    similar_joboffers = None

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
        return self.joboffer_position_text
        
    def get_meta_description(self):
        if self.joboffer_lead:
            return strip_tags(self.joboffer_lead)

    def get_meta_image(self):
        if self.joboffer_image:
            return self.build_absolute_uri(self.joboffer_image.url)
        
    def joboffer_position_safe(self):
        return mark_safe(self.joboffer_position)     
    
    @property
    def joboffer_related_objects(self):
        if self.related_objects is None:
            self.related_objects = list()
            for p in self.joboffer_connected_projects.all().order_by('project_date_add'):
                r = RelatedObject(p.project_title, p.project_lead, p.project_image, p.project_date_add, 'project',
                                  p.get_absolute_url())
                self.related_objects.append(r)
            
            self.related_objects.sort(key=lambda ro : ro.date_add, reverse=True)
        
        return self.related_objects
    
    @property
    def joboffer_similar_joboffers(self):
        if self.similar_joboffers is None:
            self.similar_joboffers = list()
            more_like_this_joboffers = SearchQuerySet().models(JobOffer).more_like_this(self)
            i = 0;
            for joboffer in more_like_this_joboffers:
                if joboffer.object is None:
                    continue
                jo = RelatedObject(joboffer.object.joboffer_position, joboffer.object.joboffer_lead, joboffer.object.joboffer_image,
                                  joboffer.object.joboffer_date_add, None, joboffer.object.get_absolute_url())
                self.similar_joboffers.append(jo)
                i = i + 1
                if i >= MAX_NUMBER_OF_SIMILAR_ENTITIES:
                    break
            
        return self.similar_joboffers    
    
    def __unicode__(self):
        return u'%s' % (self.joboffer_position_text)
     
    def __str__(self):
        return self.joboffer_position_text
     
    def clean(self):
        can_add = True
        if self.joboffer_is_promoted:
            qrs = JobOffer.objects.filter(joboffer_is_promoted=True).exclude(joboffer_id=self.joboffer_id)
            can_add = (qrs.count() < MAX_NUMBER_OF_PROMOTED_ENTITIES);
        if not can_add:
            raise ValidationError(MessageJobOffer.TO_MANY_PROMOTED)
        models.Model.clean(self)
    
    def get_absolute_url(self):
        return "/" + BPORTAL_BASE_URL + "joboffers/%s,%d/details" % (self.joboffer_position_slug, self.joboffer_id)
         
    class Meta:
        ordering = ('joboffer_position_text',)
        verbose_name = FieldJobOffer.VERBOSE_NAME
        verbose_name_plural = FieldJobOffer.VERBOSE_NAME_PLURAL


@reversion.register
class JobOfferFile(models.Model):
    
    def joboffer_files(self, filename):
        currDate = date.today()
        year = str(currDate.year)
        month = str(currDate.month)
        url = "joboffers/files/%s/%s/%s" % (year, month, filename)
        return url
     
    joboffer = models.ForeignKey(JobOffer, verbose_name=FieldJobOfferFile.JOB_OFFER, related_name='joboffer_files')
    file = models.FileField(FieldJobOfferFile.FILE, upload_to=joboffer_files)
    copyright = models.TextField(FieldJobOfferFile.COPYRIGHT, null=True, blank=True)
         
    def __unicode__(self):
        return u'%s' % (basename(self.file.name))
    
    def __str__(self):
        return '%s' % (basename(self.file.name))
     
    class Meta:
        verbose_name = FieldJobOfferFile.VERBOSE_NAME
        verbose_name_plural = FieldJobOfferFile.VERBOSE_NAME_PLURAL


@reversion.register
class JobOfferLink(models.Model):
    joboffer = models.ForeignKey(JobOffer, verbose_name=FieldJobOfferLink.JOB_OFFER, related_name='joboffer_links')
    link = models.URLField(FieldJobOfferLink.LINK, null=True, blank=True)
    
    def __unicode__(self):
        return u'%s' % (self.link)
    
    def __str__(self):
        return '%s' % (self.link)
    
    class Meta(object):
        verbose_name = FieldJobOfferLink.VERBOSE_NAME
        verbose_name_plural = FieldJobOfferLink.VERBOSE_NAME_PLURAL


@reversion.register
class JobOfferContentContribution(models.Model):
    joboffer = models.ForeignKey(JobOffer, verbose_name=FieldJobOfferContentContribution.JOB_OFFER, related_name='joboffer_content_contributors')
    person = models.ForeignKey(Person, verbose_name=FieldJobOfferContentContribution.PERSON)
    role = models.ForeignKey(PersonContributionRole, verbose_name=FieldJobOfferContentContribution.ROLE)
        
    def __unicode__(self):
        return u'%s %s' % (self.joboffer.joboffer_position_text, self.person.person_last_name)
    
    def __str__(self):
        return '%s %s' % (self.joboffer.joboffer_position_text, self.person.person_last_name)
    
    class Meta(object):
        unique_together = (('joboffer', 'person'),)
        verbose_name = FieldJobOfferContentContribution.VERBOSE_NAME
        verbose_name_plural = FieldJobOfferContentContribution.VERBOSE_NAME_PLURAL


class JobOfferAuthorized(models.Model):
    joboffer = models.ForeignKey(JobOffer, verbose_name=FieldJobOfferAuthorized.JOB_OFFER)
    authorized = models.ForeignKey(Institution, verbose_name=FieldJobOfferAuthorized.AUTHORIZED)
        
    def __unicode__(self):
        return u'%s %s' % (self.joboffer.joboffer_position_text, self.authorized.institution_shortname)
    
    def __str__(self):
        return '%s %s' % (self.joboffer.joboffer_position_text, self.authorized.institution_shortname)
    
    class Meta(object):
        unique_together = (('joboffer', 'authorized'),)
        verbose_name = FieldJobOfferAuthorized.VERBOSE_NAME
        verbose_name_plural = FieldJobOfferAuthorized.VERBOSE_NAME_PLURAL
        
        
class JobOfferModification(models.Model):
    joboffer = models.ForeignKey(JobOffer, verbose_name=FieldJobOfferModification.JOB_OFFER)
    user = models.ForeignKey(User, verbose_name=FieldJobOfferModification.USER)
    date_time = models.DateTimeField(FieldJobOfferModification.DATE_TIME)
    
    def __unicode__(self):
        return u'%s %s' % (self.joboffer.joboffer_position_text, self.user.username)
    
    def __str__(self):
        return '%s %s' % (self.joboffer.joboffer_position_text, self.user.username)
    
    class Meta(object):
        verbose_name = FieldJobOfferModification.VERBOSE_NAME
        verbose_name_plural = FieldJobOfferModification.VERBOSE_NAME_PLURAL         
