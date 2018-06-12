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

from .fields import FieldEducationalOfferType, FieldEducationalOfferMode, FieldEducationalOffer, FieldEducationalOfferFile, FieldEducationalOfferLink, FieldEducationalOfferContentContribution, FieldEducationalOfferAuthorized, FieldEducationalOfferModification
from .messages import MessageEducationalOffer


class EducationalOfferType(models.Model):
    type_id = models.AutoField(primary_key=True)
    type_name = models.CharField(FieldEducationalOfferType.TYPE_NAME, max_length=1250)
    
    def __unicode__(self):
        return u'%s' % (self.type_name)
    
    def __str__(self):
        return self.type_name
    
    class Meta:
        ordering = ('type_name',)
        verbose_name = FieldEducationalOfferType.VERBOSE_NAME
        verbose_name_plural = FieldEducationalOfferType.VERBOSE_NAME_PLURAL
        

class EducationalOfferMode(models.Model):
    mode_id = models.AutoField(primary_key=True)
    mode_name = models.CharField(FieldEducationalOfferMode.MODE_NAME, max_length=1250)
    
    def __unicode__(self):
        return u'%s' % (self.mode_name)
    
    def __str__(self):
        return self.mode_name
    
    class Meta:
        ordering = ('mode_name',)
        verbose_name = FieldEducationalOfferMode.VERBOSE_NAME
        verbose_name_plural = FieldEducationalOfferMode.VERBOSE_NAME_PLURAL


class TaggedEducationalOffer(TaggedItemBase):
    content_object = models.ForeignKey('EducationalOffer')
    
    def __unicode__(self):
        return u'%s' % (self.tag)
    
    def __str__(self):
        return '%s' % (self.tag)
    

@reversion.register(exclude=['eduoffer_is_promoted'], follow=['eduoffer_files', 'eduoffer_links', 'eduoffer_content_contributors'])
class EducationalOffer(ModelMeta, models.Model):

    def image_file(self, filename):
        currDate = date.today()
        year = str(currDate.year)
        month = str(currDate.month)
        url = "eduoffers/images/%s/%s/%s" % (year, month, filename)
        return url
    
    eduoffer_id = models.AutoField(primary_key=True)
    eduoffer_position = models.TextField(FieldEducationalOffer.POSITION)
    eduoffer_position_text = models.TextField(FieldEducationalOffer.POSITION)
    eduoffer_position_slug = models.SlugField(unique=False, max_length=128)
    eduoffer_lead = models.TextField(FieldEducationalOffer.LEAD, null=True, blank=False)    
    eduoffer_image = models.ImageField(FieldEducationalOffer.IMAGE, upload_to=image_file, null=True, blank=True)
    eduoffer_image_thumbnail = ImageSpecField(source='eduoffer_image', format='JPEG', options={'quality': 60})
    eduoffer_image_copyright = models.TextField(FieldEducationalOffer.IMAGE_COPYRIGHT, null=True, blank=True)
    eduoffer_image_caption = models.CharField(FieldEducationalOffer.IMAGE_CAPTION, max_length=1024, null=True, blank=True)
    eduoffer_institution = models.ForeignKey(Institution, null=True, blank=True, verbose_name=FieldEducationalOffer.INSTITUTION, related_name='institution_eduoffers')
    eduoffer_tuition = models.CharField(FieldEducationalOffer.TUITION, max_length=1024)
    eduoffer_period = models.CharField(FieldEducationalOffer.PERIOD, max_length=1024)
    eduoffer_date_start = models.DateField(FieldEducationalOffer.DATE_START, null=True, blank=True)
    eduoffer_date_end = models.DateField(FieldEducationalOffer.DATE_END, null=True, blank=True)
    eduoffer_city = models.ForeignKey(City, verbose_name=FieldEducationalOffer.CITY, null=True, blank=True)
    eduoffer_type = models.ForeignKey(EducationalOfferType, null=True, blank=True, verbose_name=FieldEducationalOffer.TYPE, related_name='eduoffertype_offers+')
    eduoffer_mode = models.ForeignKey(EducationalOfferMode, null=True, blank=True, verbose_name=FieldEducationalOffer.MODE, related_name='eduoffermode_offers+')
    eduoffer_description = models.TextField(FieldEducationalOffer.DESCRIPTION, null=False, blank=False)
    eduoffer_date_add = models.DateTimeField(FieldEducationalOffer.DATE_ADD, default=timezone.now)
    eduoffer_date_edit = models.DateTimeField(FieldEducationalOffer.DATE_EDIT, default=timezone.now)
    eduoffer_keywords = TaggableManager(verbose_name=FieldEducationalOffer.KEYWORDS, through=TaggedEducationalOffer)
    eduoffer_added_by = models.ForeignKey(User, verbose_name=FieldEducationalOffer.ADDED_BY, null=True, blank=True, related_name='user_added_eduoffers')
    eduoffer_modified_by = models.ForeignKey(User, verbose_name=FieldEducationalOffer.MODIFIED_BY, null=True, blank=True, related_name='user_modified_eduoffers')
    eduoffer_is_promoted = models.BooleanField(FieldEducationalOffer.IS_PROMOTED, default=False)
    eduoffer_is_accepted = models.BooleanField(FieldEducationalOffer.IS_ACCEPTED, default=False)
    eduoffer_authorizations = models.ManyToManyField(Institution, through='EducationalOfferAuthorized', through_fields=('eduoffer', 'authorized'), blank=True, related_name='authorization_eduoffers+')
     
    curr_page = None
    per_page = None
    filter = None
    related_objects = None
    similar_eduoffers = None    
    
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
        return self.eduoffer_position_text
        
    def get_meta_description(self):
        if self.eduoffer_lead:
            return strip_tags(self.eduoffer_lead)

    def get_meta_image(self):
        if self.eduoffer_image:
            return self.build_absolute_uri(self.eduoffer_image.url)
         
    def eduoffer_position_safe(self):
        return mark_safe(self.eduoffer_position)    
    
    @property
    def eduoffer_related_objects(self):
        if self.related_objects is None:
            self.related_objects = list()
            for p in self.eduoffer_connected_projects.all().order_by('project_date_add'):
                r = RelatedObject(p.project_title, p.project_lead, p.project_image, p.project_date_add, 'project',
                                  p.get_absolute_url())
                self.related_objects.append(r)
        
            self.related_objects.sort(key=lambda ro : ro.date_add, reverse=True)
        
        return self.related_objects

    @property
    def eduoffer_similar_eduoffers(self):
        if self.similar_eduoffers is None:
            self.similar_eduoffers = list()
            more_like_this_eduoffers = SearchQuerySet().models(EducationalOffer).more_like_this(self)
            i = 0;
            for eduoffer in more_like_this_eduoffers:
                if eduoffer.object is None:
                    continue
                eo = RelatedObject(eduoffer.object.eduoffer_position, eduoffer.object.eduoffer_lead, eduoffer.object.eduoffer_image,
                                  eduoffer.object.eduoffer_date_add, None, eduoffer.object.get_absolute_url())
                self.similar_eduoffers.append(eo)
                i = i + 1
                if i >= MAX_NUMBER_OF_SIMILAR_ENTITIES:
                    break
            
        return self.similar_eduoffers       

    def __unicode__(self):
        return u'%s' % (self.eduoffer_position_text)
     
    def __str__(self):
        return self.eduoffer_position_text
     
    def clean(self):
        can_add = True
        if self.eduoffer_is_promoted:
            qrs = EducationalOffer.objects.filter(eduoffer_is_promoted=True).exclude(eduoffer_id=self.eduoffer_id)
            can_add = (qrs.count() < MAX_NUMBER_OF_PROMOTED_ENTITIES);
        if not can_add:
            raise ValidationError(MessageEducationalOffer.TO_MANY_PROMOTED)
        models.Model.clean(self)
    
    def get_absolute_url(self):
        return "/" + BPORTAL_BASE_URL + "eduoffers/%s,%d/details" % (self.eduoffer_position_slug, self.eduoffer_id)
         
    class Meta:
        ordering = ('eduoffer_position_text',)
        verbose_name = FieldEducationalOffer.VERBOSE_NAME
        verbose_name_plural = FieldEducationalOffer.VERBOSE_NAME_PLURAL
         

@reversion.register
class EducationalOfferFile(models.Model):
    
    def eduoffers_files(self, filename):
        currDate = date.today()
        year = str(currDate.year)
        month = str(currDate.month)
        url = "eduoffers/files/%s/%s/%s" % (year, month, filename)
        return url
     
    eduoffer = models.ForeignKey(EducationalOffer, verbose_name=FieldEducationalOfferFile.EDUCATIONAL_OFFER, related_name='eduoffer_files')
    file = models.FileField(FieldEducationalOfferFile.FILE, upload_to=eduoffers_files)
    copyright = models.TextField(FieldEducationalOfferFile.COPYRIGHT, null=True, blank=True)
         
    def __unicode__(self):
        return u'%s' % (basename(self.file.name))
    
    def __str__(self):
        return '%s' % (basename(self.file.name))
     
    class Meta:
        verbose_name = FieldEducationalOfferFile.VERBOSE_NAME
        verbose_name_plural = FieldEducationalOfferFile.VERBOSE_NAME_PLURAL


@reversion.register
class EducationalOfferLink(models.Model):
    eduoffer = models.ForeignKey(EducationalOffer, verbose_name=FieldEducationalOfferLink.EDUCATIONAL_OFFER, related_name='eduoffer_links')
    link = models.URLField(FieldEducationalOfferLink.LINK, null=True, blank=True)
    
    def __unicode__(self):
        return u'%s' % (self.link)
    
    def __str__(self):
        return '%s' % (self.link)
    
    class Meta(object):
        verbose_name = FieldEducationalOfferLink.VERBOSE_NAME
        verbose_name_plural = FieldEducationalOfferLink.VERBOSE_NAME_PLURAL


@reversion.register
class EducationalOfferContentContribution(models.Model):
    eduoffer = models.ForeignKey(EducationalOffer, verbose_name=FieldEducationalOfferContentContribution.EDUCATIONAL_OFFER, related_name='eduoffer_content_contributors')
    person = models.ForeignKey(Person, verbose_name=FieldEducationalOfferContentContribution.PERSON)
    role = models.ForeignKey(PersonContributionRole, verbose_name=FieldEducationalOfferContentContribution.ROLE)
        
    def __unicode__(self):
        return u'%s %s' % (self.eduoffer.eduoffer_position_text, self.person.person_last_name)
    
    def __str__(self):
        return '%s %s' % (self.eduoffer.eduoffer_position_text, self.person.person_last_name)
    
    class Meta(object):
        unique_together = (('eduoffer', 'person'),)
        verbose_name = FieldEducationalOfferContentContribution.VERBOSE_NAME
        verbose_name_plural = FieldEducationalOfferContentContribution.VERBOSE_NAME_PLURAL


class EducationalOfferAuthorized(models.Model):
    eduoffer = models.ForeignKey(EducationalOffer, verbose_name=FieldEducationalOfferAuthorized.EDUCATIONAL_OFFER)
    authorized = models.ForeignKey(Institution, verbose_name=FieldEducationalOfferAuthorized.AUTHORIZED)
        
    def __unicode__(self):
        return u'%s %s' % (self.eduoffer.eduoffer_position_text, self.eduoffer.eduoffer_institution)
    
    def __str__(self):
        return '%s %s' % (self.eduoffer.eduoffer_position_text, self.eduoffer.eduoffer_institution)
    
    class Meta(object):
        unique_together = (('eduoffer', 'authorized'),)
        verbose_name = FieldEducationalOfferAuthorized.VERBOSE_NAME
        verbose_name_plural = FieldEducationalOfferAuthorized.VERBOSE_NAME_PLURAL 
        
        
class EducationalOfferModification(models.Model):
    eduoffer = models.ForeignKey(EducationalOffer, verbose_name=FieldEducationalOfferModification.EDUCATIONAL_OFFER)
    user = models.ForeignKey(User, verbose_name=FieldEducationalOfferModification.USER)
    date_time = models.DateTimeField(FieldEducationalOfferModification.DATE_TIME)
    
    def __unicode__(self):
        return u'%s %s' % (self.eduoffer.eduoffer_position_text, self.user.username)
    
    def __str__(self):
        return '%s %s' % (self.eduoffer.eduoffer_position_text, self.user.username)
    
    class Meta(object):
        verbose_name = FieldEducationalOfferModification.VERBOSE_NAME
        verbose_name_plural = FieldEducationalOfferModification.VERBOSE_NAME_PLURAL
        
