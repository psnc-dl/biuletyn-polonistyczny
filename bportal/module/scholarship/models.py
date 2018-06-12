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
from bportal.module.institution.models import Institution
from bportal.module.person.models import Person, PersonContributionRole
from bportal.settings import BPORTAL_BASE_URL

from .fields import FieldScholarship, FieldScholarshipType, FieldScholarshipFile, FieldScholarshipLink, FieldScholarshipContentContribution, FieldScholarshipAuthorized, FieldScholarshipModification
from .messages import MessageScholarship


class ScholarshipType(models.Model):
    type_id = models.AutoField(primary_key=True)
    type_name = models.CharField(FieldScholarshipType.TYPE_NAME, max_length=1024)
    
    def __unicode__(self):
        return u'%s' % (self.type_name)
    
    def __str__(self):
        return self.type_name
    
    class Meta:
        ordering = ('type_name',)
        verbose_name = FieldScholarshipType.VERBOSE_NAME
        verbose_name_plural = FieldScholarshipType.VERBOSE_NAME_PLURAL


class TaggedScholarsihp(TaggedItemBase):
    content_object = models.ForeignKey('Scholarship')
    
    def __unicode__(self):
        return u'%s' % (self.tag)
    
    def __str__(self):
        return '%s' % (self.tag)


@reversion.register(exclude=['scholarship_is_promoted'], follow=['scholarship_files', 'scholarship_links', 'scholarship_content_contributors'])
class Scholarship(ModelMeta, models.Model):
    
    def image_file(self, filename):
        currDate = date.today()
        year = str(currDate.year)
        month = str(currDate.month)
        url = "scholarships/images/%s/%s/%s" % (year, month, filename)
        return url
    
    scholarship_id = models.AutoField(primary_key=True)
    scholarship_name = models.TextField(FieldScholarship.NAME)
    scholarship_name_text = models.TextField(FieldScholarship.NAME)
    scholarship_name_slug = models.SlugField(unique=False, max_length=128)
    scholarship_lead = models.TextField(FieldScholarship.LEAD, null=True, blank=False)    
    scholarship_image = models.ImageField(FieldScholarship.IMAGE, upload_to=image_file, null=True, blank=True)
    scholarship_image_thumbnail = ImageSpecField(source='scholarship_image', format='JPEG', options={'quality': 60})
    scholarship_image_copyright = models.TextField(FieldScholarship.IMAGE_COPYRIGHT, null=True, blank=True)
    scholarship_image_caption = models.CharField(FieldScholarship.IMAGE_CAPTION, max_length=1024, null=True, blank=True)
    scholarship_founder = models.ForeignKey(Institution, null=True, blank=True, verbose_name=FieldScholarship.FOUNDER, related_name='institution_scholarships')
    scholarship_targets = models.ManyToManyField(TargetGroup, verbose_name=FieldScholarship.TARGETS, blank=True, related_name='target_scholarships+')
    scholarship_description = models.TextField(FieldScholarship.DESCRIPTION, null=False, blank=False)
    scholarship_date_start = models.DateField(FieldScholarship.DATE_START, null=True, blank=True)
    scholarship_date_end = models.DateField(FieldScholarship.DATE_END, null=True, blank=True)
    scholarship_city = models.ForeignKey(City, verbose_name=FieldScholarship.CITY, null=True, blank=True)
    scholarship_type = models.ForeignKey(ScholarshipType, null=True, blank=True, verbose_name=FieldScholarship.TYPE, related_name='type_scholarships+')
    scholarship_date_add = models.DateTimeField(FieldScholarship.DATE_ADD, default=timezone.now)
    scholarship_date_edit = models.DateTimeField(FieldScholarship.DATE_EDIT, default=timezone.now)
    scholarship_keywords = TaggableManager(verbose_name=FieldScholarship.KEYWORDS, through=TaggedScholarsihp)
    scholarship_added_by = models.ForeignKey(User, verbose_name=FieldScholarship.ADDED_BY , null=True, blank=True, related_name='user_added_scholarships')
    scholarship_modified_by = models.ForeignKey(User, verbose_name=FieldScholarship.MODIFIED_BY, null=True, blank=True, related_name='user_modified_scholarships')
    scholarship_is_promoted = models.BooleanField(FieldScholarship.IS_PROMOTED, default=False)
    scholarship_is_accepted = models.BooleanField(FieldScholarship.IS_ACCEPTED, default=False)
    scholarship_authorizations = models.ManyToManyField(Institution, through='ScholarshipAuthorized', through_fields=('scholarship', 'authorized'), blank=True, related_name='authorization_scholarships+')
    
    curr_page = None
    per_page = None
    filter = None
    related_objects = None
    similar_scholarships = None
    
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
        return self.scholarship_name_text
        
    def get_meta_description(self):
        if self.scholarship_lead:
            return strip_tags(self.scholarship_lead)

    def get_meta_image(self):
        if self.scholarship_image:
            return self.build_absolute_uri(self.scholarship_image.url)
        
    def scholarship_name_safe(self):
        return mark_safe(self.scholarship_name)    
    
    @property
    def scholarship_related_objects(self):
        if self.related_objects is None:
            self.related_objects = list()
            for p in self.scholarship_connected_projects.all().order_by('project_date_add'):
                r = RelatedObject(p.project_title, p.project_lead, p.project_image, p.project_date_add, 'project',
                                  p.get_absolute_url())
                self.related_objects.append(r)
        
            self.related_objects.sort(key=lambda ro : ro.date_add, reverse=True)
        
        return self.related_objects
    
    @property
    def scholarship_similar_scholarships(self):
        if self.similar_scholarships is None:
            self.similar_scholarships = list()
            more_like_this_scholarships = SearchQuerySet().models(Scholarship).more_like_this(self)
            i = 0;
            for scholarship in more_like_this_scholarships:
                if scholarship.object is None:
                    continue
                s = RelatedObject(scholarship.object.scholarship_name, scholarship.object.scholarship_lead, scholarship.object.scholarship_image,
                                  scholarship.object.scholarship_date_add, None, scholarship.object.get_absolute_url())
                self.similar_scholarships.append(s)
                i = i + 1
                if i >= MAX_NUMBER_OF_SIMILAR_ENTITIES:
                    break
        
        print(self.similar_scholarships)
        return self.similar_scholarships        
    
    def __unicode__(self):
        return u'%s' % (self.scholarship_name_text)
     
    def __str__(self):
        return self.scholarship_name_text
     
    def clean(self):
        can_add = True
        if self.scholarship_is_promoted:
            qrs = Scholarship.objects.filter(scholarship_is_promoted=True).exclude(scholarship_id=self.scholarship_id)
            can_add = (qrs.count() < MAX_NUMBER_OF_PROMOTED_ENTITIES);
        if not can_add:
            raise ValidationError(MessageScholarship.TO_MANY_PROMOTED)
        models.Model.clean(self)
        
    def get_absolute_url(self):
        return "/" + BPORTAL_BASE_URL + "scholarships/%s,%d/details" % (self.scholarship_name_slug, self.scholarship_id)
         
    class Meta:
        ordering = ('scholarship_name_text',)
        verbose_name = FieldScholarship.VERBOSE_NAME
        verbose_name_plural = FieldScholarship.VERBOSE_NAME_PLURAL
 

@reversion.register
class ScholarshipFile(models.Model):
    
    def scholarships_files(self, filename):
        currDate = date.today()
        year = str(currDate.year)
        month = str(currDate.month)
        url = "scholarships/files/%s/%s/%s" % (year, month, filename)
        return url
     
    scholarship = models.ForeignKey(Scholarship, verbose_name=FieldScholarshipFile.SCHOLARSHIP, related_name='scholarship_files')
    file = models.FileField(FieldScholarshipFile.FILE, upload_to=scholarships_files)
    copyright = models.TextField(FieldScholarshipFile.COPYRIGHT, null=True, blank=True)
         
    def __unicode__(self):
        return u'%s' % (basename(self.file.name))
    
    def __str__(self):
        return '%s' % (basename(self.file.name))
     
    class Meta:
        verbose_name = FieldScholarshipFile.VERBOSE_NAME
        verbose_name_plural = FieldScholarshipFile.VERBOSE_NAME_PLURAL
        

@reversion.register
class ScholarshipLink(models.Model):
    scholarship = models.ForeignKey(Scholarship, verbose_name=FieldScholarshipLink.SCHOLARSHIP, related_name='scholarship_links')
    link = models.URLField(FieldScholarshipLink.LINK, null=True, blank=True)
    
    def __unicode__(self):
        return u'%s' % (self.link)
    
    def __str__(self):
        return '%s' % (self.link)
    
    class Meta(object):
        verbose_name = FieldScholarshipLink.VERBOSE_NAME
        verbose_name_plural = FieldScholarshipLink.VERBOSE_NAME_PLURAL        


@reversion.register
class ScholarshipContentContribution(models.Model):
    scholarship = models.ForeignKey(Scholarship, verbose_name=FieldScholarshipContentContribution.SCHOLARSHIP, related_name='scholarship_content_contributors')
    person = models.ForeignKey(Person, verbose_name=FieldScholarshipContentContribution.PERSON)
    role = models.ForeignKey(PersonContributionRole, verbose_name=FieldScholarshipContentContribution.ROLE)
        
    def __unicode__(self):
        return u'%s %s' % (self.scholarship.scholarship_name_text, self.person.person_last_name)
    
    def __str__(self):
        return '%s %s' % (self.scholarship.scholarship_name_text, self.person.person_last_name)
    
    class Meta(object):
        unique_together = (('scholarship', 'person'),)
        verbose_name = FieldScholarshipContentContribution.VERBOSE_NAME
        verbose_name_plural = FieldScholarshipContentContribution.VERBOSE_NAME_PLURAL


class ScholarshipAuthorized(models.Model):
    scholarship = models.ForeignKey(Scholarship, verbose_name=FieldScholarshipAuthorized.SCHOLARSHIP)
    authorized = models.ForeignKey(Institution, verbose_name=FieldScholarshipAuthorized.AUTHORIZED)
        
    def __unicode__(self):
        return u'%s %s' % (self.scholarship.scholarship_name_text, self.sholarship.scholarship_institution)
    
    def __str__(self):
        return '%s %s' % (self.scholarship.scholarship_name_text, self.scholarship.scholarship_institution)
    
    class Meta(object):
        unique_together = (('scholarship', 'authorized'),)
        verbose_name = FieldScholarshipAuthorized.VERBOSE_NAME
        verbose_name_plural = FieldScholarshipAuthorized.VERBOSE_NAME_PLURAL 


class ScholarshipModification(models.Model):
    scholarship = models.ForeignKey(Scholarship, verbose_name=FieldScholarshipModification.SCHOLARSHIP)
    user = models.ForeignKey(User, verbose_name=FieldScholarshipModification.USER)
    date_time = models.DateTimeField(FieldScholarshipModification.DATE_TIME)
    
    def __unicode__(self):
        return u'%s %s' % (self.scholarship.scholarship_name_text, self.user.username)
    
    def __str__(self):
        return '%s %s' % (self.scholarship.scholarship_name_text, self.user.username)
    
    class Meta(object):
        verbose_name = FieldScholarshipModification.VERBOSE_NAME
        verbose_name_plural = FieldScholarshipModification.VERBOSE_NAME_PLURAL
