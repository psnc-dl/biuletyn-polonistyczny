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

from bportal.module.common.constants import MAX_NUMBER_OF_PROMOTED_ARTICLES, MAX_NUMBER_OF_SIMILAR_ENTITIES
from bportal.module.common.models import RelatedObject
from bportal.module.institution.models import Institution
from bportal.module.person.models import Person, PersonContributionRole
from bportal.settings import BPORTAL_BASE_URL

from .fields import FieldArticle, FieldArticleFile, FieldArticleLink, FieldArticleContentContribution, FieldArticleAuthorized, FieldArticleModification
from .messages import MessageArticle


class TaggedArticle(TaggedItemBase):
    content_object = models.ForeignKey('Article')
    
    def __unicode__(self):
        return u'%s' % (self.tag)
    
    def __str__(self):
        return '%s' % (self.tag)
   

@reversion.register(exclude=['article_is_promoted'], follow=['article_files', 'article_links', 'article_content_contributors'])
class Article(ModelMeta, models.Model):
    
    def image_file(self, filename):
        currDate = date.today()
        year = str(currDate.year)
        month = str(currDate.month)
        url = "articles/images/%s/%s/%s" % (year, month, filename)
        return url
    
    article_id = models.AutoField(primary_key=True)
    article_title = models.TextField(FieldArticle.TITLE)
    article_title_text = models.TextField(FieldArticle.TITLE)
    article_title_slug = models.SlugField(unique=False, max_length=128)
    article_lead = models.TextField(FieldArticle.LEAD, null=True, blank=False)        
    article_image = models.ImageField(FieldArticle.IMAGE, upload_to=image_file, null=True, blank=True)
    article_image_thumbnail = ImageSpecField(source='article_image', format='JPEG', options={'quality': 60})
    article_image_copyright = models.TextField(FieldArticle.IMAGE_COPYRIGHT, null=True, blank=True)
    article_image_caption = models.CharField(FieldArticle.IMAGE_CAPTION, max_length=1024, null=True, blank=True)
    article_contributors = models.ManyToManyField(Person, through='ArticleContentContribution', through_fields=('article', 'person'), blank=True, related_name='person_contributed_articles')    
    article_description = models.TextField(FieldArticle.DESCRIPTION, null=False, blank=False)
    article_date_add = models.DateTimeField(FieldArticle.DATE_ADD, default=timezone.now)
    article_date_edit = models.DateTimeField(FieldArticle.DATE_EDIT, default=timezone.now)
    article_keywords = TaggableManager(verbose_name=FieldArticle.KEYWORDS, through=TaggedArticle)
    article_added_by = models.ForeignKey(User, verbose_name=FieldArticle.ADDED_BY, null=True, blank=True, related_name='user_added_Articles')
    article_modified_by = models.ForeignKey(User, verbose_name=FieldArticle.MODIFIED_BY, null=True, blank=True, related_name='user_modified_Articles')  
    article_is_accepted = models.BooleanField(FieldArticle.IS_ACCEPTED, default=False)
    article_is_promoted = models.BooleanField(FieldArticle.IS_PROMOTED, default=False)
    article_authorizations = models.ManyToManyField(Institution, through='ArticleAuthorized', through_fields=('article', 'authorized'), blank=True, related_name='authorization_articles+')
    
    curr_page = None
    per_page = None
    filter = None
    similar_articles = None
    
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
        return self.article_title_text
        
    def get_meta_description(self):
        if self.article_lead:
            return strip_tags(self.article_lead)

    def get_meta_image(self):
        if self.article_image:
            return self.build_absolute_uri(self.article_image.url)
        
    def article_title_safe(self):
        return mark_safe(self.article_title)
        
    @property
    def article_similar_articles(self):
        if self.similar_articles is None:
            self.similar_articles = list()
            more_like_this_articles = SearchQuerySet().models(Article).more_like_this(self)
            i = 0;
            for article in more_like_this_articles:
                if article.object is None:
                    continue
                c = RelatedObject(article.object.article_title, article.object.article_lead, article.object.article_image,
                                  article.object.article_date_add, None, article.object.get_absolute_url())
                self.similar_articles.append(c)
                i = i + 1
                if i >= MAX_NUMBER_OF_SIMILAR_ENTITIES:
                    break
            
        return self.similar_articles 
       
    def __unicode__(self):
        return u'%s' % (self.article_title_text)
     
    def __str__(self):
        return self.article_title_text       

    def clean(self):
        can_add = True
        if self.article_is_promoted:
            qrs = Article.objects.filter(article_is_promoted=True).exclude(article_id=self.article_id)
            can_add = (qrs.count() < MAX_NUMBER_OF_PROMOTED_ARTICLES);
        if not can_add:
            raise ValidationError(MessageArticle.TO_MANY_PROMOTED)
        models.Model.clean(self)
    
    def get_absolute_url(self):   
        return "/" + BPORTAL_BASE_URL + "articles/%s,%d/details" % (self.article_title_slug, self.article_id)
    
    class Meta:
        ordering = ('article_title_text',)
        verbose_name = FieldArticle.VERBOSE_NAME
        verbose_name_plural = FieldArticle.VERBOSE_NAME_PLURAL


@reversion.register     
class ArticleFile(models.Model):

    def article_files(self, filename):
        currDate = date.today()
        year = str(currDate.year)
        month = str(currDate.month)
        url = "articles/files/%s/%s/%s" % (year, month, filename)
        return url
    
    article = models.ForeignKey(Article, verbose_name=FieldArticleFile.ARTICLE, related_name='article_files')
    file = models.FileField(FieldArticleFile.FILE, upload_to=article_files)
    copyright = models.TextField(FieldArticleFile.COPYRIGHT, null=True, blank=True)
    
    def __unicode__(self):
        return u'%s' % (basename(self.file.name))
    
    def __str__(self):
        return '%s' % (basename(self.file.name))
    
    class Meta(object):
        verbose_name = FieldArticleFile.VERBOSE_NAME
        verbose_name_plural = FieldArticleFile.VERBOSE_NAME_PLURAL
        

@reversion.register 
class ArticleLink(models.Model):
    article = models.ForeignKey(Article, verbose_name=FieldArticleLink.ARTICLE, related_name='article_links')
    link = models.URLField(FieldArticleLink.LINK, null=True, blank=True)
    
    def __unicode__(self):
        return u'%s' % (self.link)
    
    def __str__(self):
        return '%s' % (self.link)
    
    class Meta(object):
        verbose_name = FieldArticleLink.VERBOSE_NAME
        verbose_name_plural = FieldArticleLink.VERBOSE_NAME_PLURAL


@reversion.register
class ArticleContentContribution(models.Model):
    article = models.ForeignKey(Article, verbose_name=FieldArticleContentContribution.ARTICLE, related_name='article_content_contributors')
    person = models.ForeignKey(Person, verbose_name=FieldArticleContentContribution.PERSON)
    role = models.ForeignKey(PersonContributionRole, verbose_name=FieldArticleContentContribution.ROLE)
        
    def __unicode__(self):
        return u'%s %s' % (self.article.article_title_text, self.person.person_last_name)

    def __str__(self):
        return '%s %s' % (self.article.article_title_text, self.person.person_last_name)
    
    class Meta(object):
        unique_together = (('article', 'person'),)
        verbose_name = FieldArticleContentContribution.VERBOSE_NAME
        verbose_name_plural = FieldArticleContentContribution.VERBOSE_NAME_PLURAL


class ArticleAuthorized(models.Model):
    article = models.ForeignKey(Article, verbose_name=FieldArticleAuthorized.ARTICLE)
    authorized = models.ForeignKey(Institution, verbose_name=FieldArticleAuthorized.AUTHORIZED)
        
    def __unicode__(self):
        return u'%s %s' % (self.article.article_title_text, self.authorized.institution_shortname)
    
    def __str__(self):
        return '%s %s' % (self.article.article_title_text, self.authorized.institution_shortname)
    
    class Meta(object):
        unique_together = (('article', 'authorized'),)
        verbose_name = FieldArticleAuthorized.VERBOSE_NAME
        verbose_name_plural = FieldArticleAuthorized.VERBOSE_NAME_PLURAL
        

class ArticleModification(models.Model):
    article = models.ForeignKey(Article, verbose_name=FieldArticleModification.ARTICLE)
    user = models.ForeignKey(User, verbose_name=FieldArticleModification.USER)
    date_time = models.DateTimeField(FieldArticleModification.DATE_TIME)
    
    def __unicode__(self):
        return u'%s %s' % (self.article.article_title_text, self.user.username)
    
    def __str__(self):
        return '%s %s' % (self.article.article_title_text, self.user.username)
    
    class Meta(object):
        verbose_name = FieldArticleModification.VERBOSE_NAME
        verbose_name_plural = FieldArticleModification.VERBOSE_NAME_PLURAL
