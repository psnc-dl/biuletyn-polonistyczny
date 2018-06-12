# -*- coding: utf-8 -*-
from datetime import date
from os.path import basename

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
from bportal.module.common.models import PublicationCategory, RelatedObject
from bportal.module.institution.models import Institution
from bportal.module.person.models import Person, PersonContributionRole
from bportal.settings import BPORTAL_BASE_URL

from .fields import FieldJournal, FieldJournalIssue, FieldJournalIssueFile, FieldJournalIssueLink, FieldJournalIssueContentContribution, FieldJournalIssueModification, FieldJournalIssueAuthorized
from .messages import MessageJournalIssue


@reversion.register
class Journal(models.Model):
    
    def image_file(self, filename):
        url = "institutions/images/%s" % (filename)
        return url
    
    journal_id = models.AutoField(primary_key=True)
    journal_title = models.TextField(FieldJournal.TITLE)
    journal_title_text = models.TextField(FieldJournal.TITLE)
    journal_title_slug = models.SlugField(unique=False, max_length=128)     
    journal_lead = models.TextField(FieldJournal.LEAD, null=True, blank=False)
    journal_publisher = models.ForeignKey(Institution, verbose_name=FieldJournal.PUBLISHER, null=True, blank=True, related_name='institution_journals')
    journal_categories = models.ManyToManyField(PublicationCategory, verbose_name=FieldJournal.CATEGORIES, blank=True, related_name='publication_category_journals+')
    journal_editorial_office = models.TextField(FieldJournal.EDITORIAL_OFFICE, null=True, blank=False)
    journal_editor_in_chief = models.ForeignKey(Person, verbose_name=FieldJournal.EDITOR_IN_CHIEF, related_name='person_journals', null=True, blank=True)
    journal_first_issue_date = models.DateTimeField(FieldJournal.FIRST_ISSUE_DATE, null=True, blank=True)
    
    def journal_title_safe(self):
        return mark_safe(self.journal_title)
    
    def __unicode__(self):
        return u'%s' % (self.journal_title_text)
    
    def __str__(self):
        return self.journal_title_text
        
    def get_absolute_url(self):
        return "/" + BPORTAL_BASE_URL + "journals/%s,%d/details" % (self.journal_title_slug, self.journal_id)
          
    class Meta:
        ordering = ('journal_title_text',)
        verbose_name = FieldJournal.VERBOSE_NAME
        verbose_name_plural = FieldJournal.VERBOSE_NAME_PLURAL


class TaggedJournalIssue(TaggedItemBase):
    content_object = models.ForeignKey('JournalIssue')
    
    def __unicode__(self):
        return u'%s' % (self.tag)
    
    def __str__(self):
        return '%s' % (self.tag)


@reversion.register(exclude=['journalissue_is_promoted'], follow=['journalissue_files', 'journalissue_links', 'journalissue_content_contributors'])
class JournalIssue(ModelMeta, models.Model):
    
    def image_file(self, filename):
        currDate = date.today()
        year = str(currDate.year)
        month = str(currDate.month)
        url = "journals/issues/images/%s/%s/%s" % (year, month, filename)
        return url
        
    journalissue_id = models.AutoField(primary_key=True)
    journalissue_title = models.TextField(FieldJournalIssue.TITLE)
    journalissue_title_text = models.TextField(FieldJournalIssue.TITLE)
    journalissue_title_slug = models.SlugField(unique=False, max_length=128)     
    journalissue_lead = models.TextField(FieldJournalIssue.LEAD, null=True, blank=False)
    journalissue_image = models.ImageField(FieldJournalIssue.IMAGE, upload_to=image_file, null=True, blank=True)
    journalissue_image_thumbnail = ImageSpecField(source='journalissue_image', format='JPEG', options={'quality': 60})
    journalissue_image_copyright = models.TextField(FieldJournalIssue.IMAGE_COPYRIGHT, null=True, blank=True)
    journalissue_image_caption = models.CharField(FieldJournalIssue.IMAGE_CAPTION, max_length=1024, null=True, blank=True)
    journalissue_category = models.ForeignKey(PublicationCategory, verbose_name=FieldJournalIssue.CATEGORY, null=False, blank=False, related_name='publication_category_journalsissues+')
    journalissue_description = models.TextField(FieldJournalIssue.DESCRIPTION, null=False, blank=False)
    journalissue_table_of_contents = models.TextField(FieldJournalIssue.TABLE_OF_CONTENTS, null=True, blank=True)
    journalissue_journal = models.ForeignKey(Journal, null=False, blank=False, verbose_name=FieldJournalIssue.JOURNAL, related_name='journal_journalissues')
    journalissue_publisher = models.ForeignKey(Institution, null=True, blank=True, verbose_name=FieldJournalIssue.PUBLISHER, related_name='institution_journalissues')
    journalissue_issn = models.CharField(FieldJournalIssue.ISSN, max_length=64, null=True, blank=True)
    journalissue_year = models.CharField(FieldJournalIssue.YEAR, max_length=64, null=True, blank=False)
    journalissue_volume = models.CharField(FieldJournalIssue.VOLUME, max_length=64, null=True, blank=True)
    journalissue_number = models.CharField(FieldJournalIssue.NUMBER, max_length=64, null=True, blank=True)
    journalissue_publication_date = models.DateField(FieldJournalIssue.PUBLICATION_DATE, null=True, blank=True)
    journalissue_pages = models.CharField(FieldJournalIssue.PAGES, max_length=64, null=True, blank=True)
    journalissue_date_add = models.DateTimeField(FieldJournalIssue.DATE_ADD, default=timezone.now)
    journalissue_date_edit = models.DateTimeField(FieldJournalIssue.DATE_EDIT, default=timezone.now)
    journalissue_keywords = TaggableManager(verbose_name=FieldJournalIssue.KEYWORDS, through=TaggedJournalIssue)
    journalissue_added_by = models.ForeignKey(User, verbose_name=FieldJournalIssue.ADDED_BY, null=True, blank=True, related_name='user_added_journalsissues')
    journalissue_modified_by = models.ForeignKey(User, verbose_name=FieldJournalIssue.MODIFIED_BY, null=True, blank=True, related_name='user_modified_journalsissues')
    journalissue_is_accepted = models.BooleanField(FieldJournalIssue.IS_ACCEPTED, default=False)
    journalissue_is_promoted = models.BooleanField(FieldJournalIssue.IS_PROMOTED, default=False)
    journalissue_authorizations = models.ManyToManyField(Institution, through='JournalIssueAuthorized', through_fields=('journalissue', 'authorized'), blank=True, related_name='authorization_journalsissues+')
        
    curr_page = None
    per_page = None
    filter = None
    similar_journalissues = None 

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
        return self.journalissue_title_text
        
    def get_meta_description(self):
        if self.journalissue_lead:
            return strip_tags(self.journalissue_lead)

    def get_meta_image(self):
        if self.journalissue_image:
            return self.build_absolute_uri(self.journalissue_image.url)
       
    def journalissue_title_safe(self):
        return mark_safe(self.journalissue_title)

    @property
    def journalissue_similar_journalissues(self):
        if self.similar_journalissues is None:
            self.similar_journalissues = list()
            more_like_this_journalissues = SearchQuerySet().models(JournalIssue).more_like_this(self)
            i = 0;
            for journalissue in more_like_this_journalissues:
                if journalissue.object is None:
                    continue
                title = journalissue.object.journalissue_journal.journal_title
                title = title + ' | '
                if journalissue.object.journalissue_volume:
                    title = title + journalissue.object.journalissue_volume 
                if journalissue.object.journalissue_number:
                    title = title + '(' + journalissue.object.journalissue_number + ')'
                title = title + ' | '
                title = title + journalissue.object.journalissue_year
                b = RelatedObject(title, journalissue.object.journalissue_lead, journalissue.object.journalissue_image,
                                  journalissue.object.journalissue_date_add, journalissue.object.journalissue_category.publication_category_name, journalissue.object.get_absolute_url(),
                                  journalissue.object.journalissue_title)
                self.similar_journalissues.append(b)
                i = i + 1
                if i >= MAX_NUMBER_OF_SIMILAR_ENTITIES - 1:
                    break
            
        return self.similar_journalissues   
    
    def __unicode__(self):
        return u'%s' % (self.journalissue_title_text)
     
    def __str__(self):
        return self.journalissue_title_text
     
    def clean(self):
        can_add = True
        if self.journalissue_is_promoted:
            qrs = JournalIssue.objects.filter(journalissue_is_promoted=True).exclude(journalissue_id=self.journalissue_id)
            can_add = (qrs.count() < MAX_NUMBER_OF_PROMOTED_ENTITIES);
        if not can_add:
            raise ValidationError(MessageJournalIssue.TO_MANY_PROMOTED)
        models.Model.clean(self)
    
    def get_absolute_url(self):
        return "/" + BPORTAL_BASE_URL + "journals/issues/%s,%d/details" % (self.journalissue_title_slug, self.journalissue_id)
             
    class Meta:
        ordering = ('journalissue_title_text',)
        verbose_name = FieldJournalIssue.VERBOSE_NAME
        verbose_name_plural = FieldJournalIssue.VERBOSE_NAME_PLURAL


@reversion.register
class JournalIssueFile(models.Model):

    def journalissue_files(self, filename):
        currDate = date.today()
        year = str(currDate.year)
        month = str(currDate.month)
        url = "journals/issues/files/%s/%s/%s" % (year, month, filename)
        return url
    
    journalissue = models.ForeignKey(JournalIssue, verbose_name=FieldJournalIssueFile.JOURNALISSUE, related_name='journalissue_files')
    file = models.FileField(FieldJournalIssueFile.FILE, upload_to=journalissue_files)
    copyright = models.TextField(FieldJournalIssueFile.COPYRIGHT, null=True, blank=True)
    
    def __unicode__(self):
        return u'%s' % (basename(self.file.name))
    
    def __str__(self):
        return '%s' % (basename(self.file.name))
    
    class Meta(object):
        verbose_name = FieldJournalIssueFile.VERBOSE_NAME
        verbose_name_plural = FieldJournalIssueFile.VERBOSE_NAME_PLURAL


@reversion.register
class JournalIssueLink(models.Model):
    journalissue = models.ForeignKey(JournalIssue, verbose_name=FieldJournalIssueLink.JOURNALISSUE, related_name='journalissue_links')
    link = models.URLField(FieldJournalIssueLink.LINK, null=True, blank=True)
    
    def __unicode__(self):
        return u'%s' % (self.link)
    
    def __str__(self):
        return '%s' % (self.link)
    
    class Meta(object):
        verbose_name = FieldJournalIssueLink.VERBOSE_NAME
        verbose_name_plural = FieldJournalIssueLink.VERBOSE_NAME_PLURAL


@reversion.register
class JournalIssueContentContribution(models.Model):
    journalissue = models.ForeignKey(JournalIssue, verbose_name=FieldJournalIssueContentContribution.JOURNALISSUE, related_name='journalissue_content_contributors')
    person = models.ForeignKey(Person, verbose_name=FieldJournalIssueContentContribution.PERSON)
    role = models.ForeignKey(PersonContributionRole, verbose_name=FieldJournalIssueContentContribution.ROLE)
        
    def __unicode__(self):
        return u'%s %s' % (self.journalissue.journalissue_title_text, self.person.person_last_name)
    
    def __str__(self):
        return '%s %s' % (self.journalissue.journalissue_title_text, self.person.person_last_name)
    
    class Meta(object):
        unique_together = (('journalissue', 'person'),)
        verbose_name = FieldJournalIssueContentContribution.VERBOSE_NAME
        verbose_name_plural = FieldJournalIssueContentContribution.VERBOSE_NAME_PLURAL


class JournalIssueAuthorized(models.Model):
    journalissue = models.ForeignKey(JournalIssue, verbose_name=FieldJournalIssueAuthorized.JOURNALISSUE)
    authorized = models.ForeignKey(Institution, verbose_name=FieldJournalIssueAuthorized.AUTHORIZED)
        
    def __unicode__(self):
        return u'%s %s' % (self.journalissue.journalissue_title_text, self.authorized.institution_shortname)
    
    def __str__(self):
        return '%s %s' % (self.journalissue.journalissue_title_text, self.authorized.institution_shortname)
    
    class Meta(object):
        unique_together = (('journalissue', 'authorized'),)
        verbose_name = FieldJournalIssueAuthorized.VERBOSE_NAME
        verbose_name_plural = FieldJournalIssueAuthorized.VERBOSE_NAME_PLURAL 


class JournalIssueModification(models.Model):
    journalissue = models.ForeignKey(JournalIssue, verbose_name=FieldJournalIssueModification.JOURNALISSUE)
    user = models.ForeignKey(User, verbose_name=FieldJournalIssueModification.USER)
    date_time = models.DateTimeField(FieldJournalIssueModification.DATE_TIME)
    
    def __unicode__(self):
        return u'%s %s' % (self.journalissue.journalissue_title_text, self.user.username)
    
    def __str__(self):
        return '%s %s' % (self.journalissue.journalissue_title_text, self.user.username)
    
    class Meta(object):
        verbose_name = FieldJournalIssueModification.VERBOSE_NAME
        verbose_name_plural = FieldJournalIssueModification.VERBOSE_NAME_PLURAL
                
