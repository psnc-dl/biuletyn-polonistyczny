# -*- coding: utf-8 -*-
from datetime import date
from os.path import basename

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from imagekit.models import ImageSpecField
from meta.models import ModelMeta
import reversion
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase

from bportal.module.article.models import Article
from bportal.module.book.models import Book
from bportal.module.common.constants import MAX_NUMBER_OF_PROMOTED_NEWS, MAX_NUMBER_OF_LATEST_NEWS
from bportal.module.common.models import RelatedObject
from bportal.module.competition.models import Competition
from bportal.module.dissertation.models import Dissertation 
from bportal.module.educationaloffer.models import EducationalOffer
from bportal.module.event.models import Event
from bportal.module.institution.models import Institution
from bportal.module.joboffer.models import JobOffer
from bportal.module.journal.models import JournalIssue
from bportal.module.person.models import Person, PersonContributionRole
from bportal.module.project.models import Project
from bportal.module.scholarship.models import Scholarship
from bportal.settings import BPORTAL_BASE_URL

from .fields import FieldNew, FieldNewCategory, FieldNewFile, FieldNewLink, FieldNewContentContribution, FieldNewAuthorized, FieldNewModification
from .messages import MessageNew  


class NewCategory(models.Model):
    new_category_id = models.AutoField(primary_key=True)
    new_category_name = models.CharField(FieldNewCategory.NAME, max_length=512)
    new_category_item_name = models.CharField(FieldNewCategory.ITEM_NAME, max_length=512)

    def __unicode__(self):
        return u'%s' % (self.new_category_name)
    
    def __str__(self):
        return self.new_category_name
           
    class Meta:
        ordering = ('new_category_name',)
        verbose_name = FieldNewCategory.VERBOSE_NAME
        verbose_name_plural = FieldNewCategory.VERBOSE_NAME_PLURAL


class TaggedNew(TaggedItemBase):
    content_object = models.ForeignKey('New')
    
    def __unicode__(self):
        return u'%s' % (self.tag)
    
    def __str__(self):
        return '%s' % (self.tag)
    

@reversion.register(exclude=['new_is_promoted'], follow=['new_files', 'new_links', 'new_content_contributors'])
class New(ModelMeta, models.Model):
    
    def image_file(self, filename):
        currDate = date.today()
        year = str(currDate.year)
        month = str(currDate.month)
        url = "news/images/%s/%s/%s" % (year, month, filename)
        return url
    
    new_id = models.AutoField(primary_key=True)
    new_title = models.TextField(FieldNew.TITLE)
    new_title_text = models.TextField(FieldNew.TITLE)
    new_title_slug = models.SlugField(unique=False, max_length=128)
    new_lead = models.TextField(FieldNew.LEAD, null=True, blank=False)     
    new_image = models.ImageField(FieldNew.IMAGE, upload_to=image_file, null=True, blank=True)
    new_image_thumbnail = ImageSpecField(source='new_image', format='JPEG', options={'quality': 60})
    new_image_copyright = models.TextField(FieldNew.IMAGE_COPYRIGHT, null=True, blank=True)
    new_image_caption = models.CharField(FieldNew.IMAGE_CAPTION, max_length=1024, null=True, blank=True)    
    new_category = models.ForeignKey(NewCategory, verbose_name=FieldNew.CATEGORY, null=True, blank=False, related_name='new_category_news')
    new_date_add = models.DateTimeField(FieldNew.DATE_ADD, default=timezone.now)
    new_date_edit = models.DateTimeField(FieldNew.DATE_EDIT, default=timezone.now)
    new_description = models.TextField(FieldNew.DESCRIPTION, null=True, blank=True)
    new_keywords = TaggableManager(verbose_name=FieldNew.KEYWORDS, through=TaggedNew, blank=True)
    new_related_event = models.ForeignKey(Event, verbose_name=FieldNew.RELATED_EVENT, null=True, blank=True, related_name='event_related_new+')
    new_related_project = models.ForeignKey(Project, verbose_name=FieldNew.RELATED_PROJECT, null=True, blank=True, related_name='project_related_new+')    
    new_related_dissertation = models.ForeignKey(Dissertation, verbose_name=FieldNew.RELATED_DISSERTATION, null=True, blank=True, related_name='dissertation_related_new+')    
    new_related_competition = models.ForeignKey(Competition, verbose_name=FieldNew.RELATED_COMPETITION, null=True, blank=True, related_name='competition_related_new+')
    new_related_joboffer = models.ForeignKey(JobOffer, verbose_name=FieldNew.RELATED_JOBOFFER, null=True, blank=True, related_name='joboffer_related_new+')    
    new_related_eduoffer = models.ForeignKey(EducationalOffer, verbose_name=FieldNew.RELATED_EDUOFFER, null=True, blank=True, related_name='eduoffer_related_new+')    
    new_related_scholarship = models.ForeignKey(Scholarship, verbose_name=FieldNew.RELATED_SCHOLARSHIP, null=True, blank=True, related_name='scholarship_related_new+')    
    new_related_book = models.ForeignKey(Book, verbose_name=FieldNew.RELATED_BOOK, null=True, blank=True, related_name='book_related_new+')
    new_related_article = models.ForeignKey(Article, verbose_name=FieldNew.RELATED_ARTICLE, null=True, blank=True, related_name='article_related_new+') 
    new_related_journalissue = models.ForeignKey(JournalIssue, verbose_name=FieldNew.RELATED_JOURNALISSUE, null=True, blank=True, related_name='journalissue_related_new+')    
    new_contributors = models.ManyToManyField(Person, through='NewContentContribution', through_fields=('new', 'person'), blank=True, related_name='person_contributed_news')
    new_added_by = models.ForeignKey(User, verbose_name=FieldNew.ADDED_BY, null=True, blank=True, related_name='user_added_news')
    new_modified_by = models.ForeignKey(User, verbose_name=FieldNew.MODIFIED_BY, null=True, blank=True, related_name='user_modified_news')
    new_is_accepted = models.BooleanField(FieldNew.IS_ACCEPTED, default=False)
    new_is_promoted = models.BooleanField(FieldNew.IS_PROMOTED, default=False)
    new_authorizations = models.ManyToManyField(Institution, through='NewAuthorized', through_fields=('new', 'authorized'), blank=True, related_name='authorization_news+')

    curr_page = None
    per_page = None
    filter = None
    latest_news = None
    
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
        return self.new_title_text
        
    def get_meta_description(self):
        if self.new_lead:
            return strip_tags(self.new_lead)

    def get_meta_image(self):
        if self.new_image:
            return self.build_absolute_uri(self.new_image.url)
        if self.new_related_event and self.new_related_event.event_poster:
            return self.build_absolute_uri(self.new_related_event.event_poster.url)
        if self.new_related_project and self.new_related_project.project_image:
            return self.build_absolute_uri(self.new_related_project.project_image.url)
        if self.new_related_dissertation and self.new_related_dissertation.dissertation_image:
            return self.build_absolute_uri(self.new_related_dissertation.dissertation_image.url)
        if self.new_related_competition and self.new_related_competition.competition_image:
            return self.build_absolute_uri(self.new_related_competition.competition_image.url)
        if self.new_related_joboffer and self.new_related_joboffer.joboffer_image:
            return self.build_absolute_uri(self.new_related_joboffer.joboffer_image.url)
        if self.new_related_eduoffer and self.new_related_eduoffer.eduoffer_image:
            return self.build_absolute_uri(self.new_related_eduoffer.eduoffer_image.url)
        if self.new_related_scholarship and self.new_related_scholarship.scholarship_image:
            return self.build_absolute_uri(self.new_related_scholarship.scholarship_image.url)
        if self.new_related_book and self.new_related_book.book_image:
            return self.build_absolute_uri(self.new_related_book.book_image.url)
        if self.new_related_journalissue and self.new_related_journalissue.journalissue_image:
            return self.build_absolute_uri(self.new_related_journalissue.journalissue_image.url)        
        if self.new_related_article and self.new_related_article.article_image:
            return self.build_absolute_uri(self.new_related_article.article_image.url)
        
    def new_title_safe(self):
        return mark_safe(self.new_title)  

    @property
    def new_latest_news(self):
        if self.latest_news is None:
            self.latest_news = list()
            limited_latest_news = New.objects.filter(new_is_accepted = True).exclude(new_id=self.new_id).order_by('-new_date_add')[:MAX_NUMBER_OF_LATEST_NEWS]
            for new in limited_latest_news:
                image = new.new_image
                if new.new_related_event and new.new_related_event.event_poster:
                    image = new.new_related_event.event_poster
                if new.new_related_project and new.new_related_project.project_image:
                    image = new.new_related_project.project_image
                if new.new_related_dissertation and new.new_related_dissertation.dissertation_image:
                    image = new.new_related_dissertation.dissertation_image
                if new.new_related_competition and new.new_related_competition.competition_image:
                    image = new.new_related_competition.competition_image
                if new.new_related_joboffer and new.new_related_joboffer.joboffer_image:
                    image = new.new_related_joboffer.joboffer_image
                if new.new_related_eduoffer and new.new_related_eduoffer.eduoffer_image:
                    image = new.new_related_eduoffer.eduoffer_image
                if new.new_related_scholarship and new.new_related_scholarship.scholarship_image:
                    image = new.new_related_scholarship.scholarship_image
                if new.new_related_book and new.new_related_book.book_image:
                    image = new.new_related_book.book_image
                if new.new_related_journalissue and new.new_related_journalissue.journalissue_image:
                    image = new.new_related_journalissue.journalissue_image   
                if new.new_related_article and new.new_related_article.article_image:
                    image = new.new_related_article.article_image                                                         
                c = RelatedObject(new.new_title, new.new_lead, image,
                                  new.new_date_add, new.new_category.new_category_item_name, new.get_absolute_url())
                self.latest_news.append(c)
            
        return self.latest_news      
    
    def __unicode__(self):
        return u'%s' % (self.new_title_text)
    
    def __str__(self):
        return self.new_title_text
        
    def clean(self):
        can_add = True
        if self.new_is_promoted:
            qrs = New.objects.filter(new_is_promoted=True).exclude(new_id=self.new_id)
            can_add = (qrs.count() < MAX_NUMBER_OF_PROMOTED_NEWS);
        if not can_add:
            raise ValidationError(MessageNew.TO_MANY_PROMOTED)
        models.Model.clean(self)

    def get_absolute_url(self):
        if self.new_related_event:
            return self.new_related_event.get_absolute_url()
        if self.new_related_project:
            return self.new_related_project.get_absolute_url()
        if self.new_related_dissertation:
            return self.new_related_dissertation.get_absolute_url()
        if self.new_related_competition:
            return self.new_related_competition.get_absolute_url()
        if self.new_related_joboffer:
            return self.new_related_joboffer.get_absolute_url()
        if self.new_related_eduoffer:
            return self.new_related_eduoffer.get_absolute_url()
        if self.new_related_scholarship:
            return self.new_related_scholarship.get_absolute_url()       
        if self.new_related_book:
            return self.new_related_book.get_absolute_url()
        if self.new_related_journalissue:
            return self.new_related_journalissue.get_absolute_url()   
        if self.new_related_article:
            return self.new_related_article.get_absolute_url()   
        return "/" + BPORTAL_BASE_URL + "news/%s,%d/details" % (self.new_title_slug, self.new_id)
        
        
    class Meta:
        ordering = ('new_title_text',)
        verbose_name = FieldNew.VERBOSE_NAME
        verbose_name_plural = FieldNew.VERBOSE_NAME_PLURAL


@reversion.register  
class NewFile(models.Model):

    def new_files(self, filename):
        currDate = date.today()
        year = str(currDate.year)
        month = str(currDate.month)
        url = "news/files/%s/%s/%s" % (year, month, filename)
        return url
    
    new = models.ForeignKey(New, verbose_name=FieldNewFile.NEW, related_name='new_files')
    file = models.FileField(FieldNewFile.FILE, upload_to=new_files)
    copyright = models.TextField(FieldNewFile.COPYRIGHT, null=True, blank=True)
    
    def __unicode__(self):
        return u'%s' % (basename(self.file.name))
    
    def __str__(self):
        return '%s' % (basename(self.file.name))
    
    class Meta(object):
        verbose_name = FieldNewFile.VERBOSE_NAME
        verbose_name_plural = FieldNewFile.VERBOSE_NAME_PLURAL
        

@reversion.register
class NewLink(models.Model):
    new = models.ForeignKey(New, verbose_name=FieldNewLink.NEW, related_name='new_links')
    link = models.URLField(FieldNewLink.LINK, null=True, blank=True)
    
    def __unicode__(self):
        return u'%s' % (self.link)
    
    def __str__(self):
        return '%s' % (self.link)
    
    class Meta(object):
        verbose_name = FieldNewLink.VERBOSE_NAME
        verbose_name_plural = FieldNewLink.VERBOSE_NAME_PLURAL


@reversion.register
class NewContentContribution(models.Model):
    new = models.ForeignKey(New, verbose_name=FieldNewContentContribution.NEW, related_name='new_content_contributors')
    person = models.ForeignKey(Person, verbose_name=FieldNewContentContribution.PERSON)
    role = models.ForeignKey(PersonContributionRole, verbose_name=FieldNewContentContribution.ROLE)
        
    def __unicode__(self):
        return u'%s %s' % (self.new.new_title_text, self.person.person_last_name)
    
    def __str__(self):
        return '%s %s' % (self.new.new_title_text, self.person.person_last_name)
    
    class Meta(object):
        unique_together = (('new', 'person'),)
        verbose_name = FieldNewContentContribution.VERBOSE_NAME
        verbose_name_plural = FieldNewContentContribution.VERBOSE_NAME_PLURAL


class NewAuthorized(models.Model):
    new = models.ForeignKey(New, verbose_name=FieldNewAuthorized.NEW)
    authorized = models.ForeignKey(Institution, verbose_name=FieldNewAuthorized.AUTHORIZED)
        
    def __unicode__(self):
        return u'%s %s' % (self.new.new_title_text, self.authorized.institution_shortname)
    
    def __str__(self):
        return '%s %s' % (self.new.new_title_text, self.authorized.institution_shortname)
    
    class Meta(object):
        unique_together = (('new', 'authorized'),)
        verbose_name = FieldNewAuthorized.VERBOSE_NAME
        verbose_name_plural = FieldNewAuthorized.VERBOSE_NAME_PLURAL
        

class NewModification(models.Model):
    new = models.ForeignKey(New, verbose_name=FieldNewModification.NEW)
    user = models.ForeignKey(User, verbose_name=FieldNewModification.USER)
    date_time = models.DateTimeField(FieldNewModification.DATE_TIME)
    
    def __unicode__(self):
        return u'%s %s' % (self.new.new_title_text, self.user.username)
    
    def __str__(self):
        return '%s %s' % (self.new.new_title_text, self.user.username)
    
    class Meta(object):
        verbose_name = FieldNewModification.VERBOSE_NAME
        verbose_name_plural = FieldNewModification.VERBOSE_NAME_PLURAL

