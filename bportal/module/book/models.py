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

from .fields import FieldBook, FieldBookFile, FieldBookLink, FieldBookContentContribution, FieldBookModification, FieldBookAuthorized
from .messages import MessageBook


class TaggedBook(TaggedItemBase):
    content_object = models.ForeignKey('Book')
    
    def __unicode__(self):
        return u'%s' % (self.tag)
    
    def __str__(self):
        return '%s' % (self.tag)
         
@reversion.register(exclude=['book_is_promoted'], follow=['book_files', 'book_links', 'book_content_contributors'])
class Book(ModelMeta, models.Model):
    
    def image_file(self, filename):
        currDate = date.today()
        year = str(currDate.year)
        month = str(currDate.month)
        url = "books/images/%s/%s/%s" % (year, month, filename)
        return url
        
    book_id = models.AutoField(primary_key=True)
    book_title = models.TextField(FieldBook.TITLE)
    book_title_text = models.TextField(FieldBook.TITLE)
    book_title_slug = models.SlugField(unique=False, max_length=128)     
    book_lead = models.TextField(FieldBook.LEAD, null=True, blank=False)
    book_image = models.ImageField(FieldBook.IMAGE, upload_to=image_file, null=True, blank=True)
    book_image_thumbnail = ImageSpecField(source='book_image', format='JPEG', options={'quality': 60})
    book_image_copyright = models.TextField(FieldBook.IMAGE_COPYRIGHT, null=True, blank=True)
    book_image_caption = models.CharField(FieldBook.IMAGE_CAPTION, max_length=1024, null=True, blank=True)
    book_authors = models.ManyToManyField(Person, verbose_name=FieldBook.AUTHORS, blank=True, related_name='person_books')
    book_category = models.ForeignKey(PublicationCategory, verbose_name=FieldBook.CATEGORY, null=False, blank=False, related_name='publication_category_books+')
    book_description = models.TextField(FieldBook.DESCRIPTION, null=False, blank=False)
    book_table_of_contents = models.TextField(FieldBook.TABLE_OF_CONTENTS, null=True, blank=True)
    book_publisher = models.ForeignKey(Institution, null=True, blank=True, verbose_name=FieldBook.PUBLISHER, related_name='institution_books')
    book_isbn = models.CharField(FieldBook.ISBN, max_length=64, null=True, blank=True)
    book_publication_date = models.DateField(FieldBook.PUBLICATION_DATE, null=True, blank=True)
    book_pages = models.CharField(FieldBook.PAGES, max_length=64, null=True, blank=True)
    book_date_add = models.DateTimeField(FieldBook.DATE_ADD, default=timezone.now)
    book_date_edit = models.DateTimeField(FieldBook.DATE_EDIT, default=timezone.now)
    book_keywords = TaggableManager(verbose_name=FieldBook.KEYWORDS, through=TaggedBook)
    book_added_by = models.ForeignKey(User, verbose_name=FieldBook.ADDED_BY, null=True, blank=True, related_name='user_added_books')
    book_modified_by = models.ForeignKey(User, verbose_name=FieldBook.MODIFIED_BY, null=True, blank=True, related_name='user_modified_books')
    book_is_accepted = models.BooleanField(FieldBook.IS_ACCEPTED, default=False)
    book_is_promoted = models.BooleanField(FieldBook.IS_PROMOTED, default=False)
    book_authorizations = models.ManyToManyField(Institution, through='BookAuthorized', through_fields=('book', 'authorized'), blank=True, related_name='authorization_books+')
        
    curr_page = None
    per_page = None
    filter = None
    similar_books = None 

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
        return self.book_title_text
        
    def get_meta_description(self):
        if self.book_lead:
            return strip_tags(self.book_lead)

    def get_meta_image(self):
        if self.book_image:
            return self.build_absolute_uri(self.book_image.url)
       
    def book_title_safe(self):
        return mark_safe(self.book_title)

    @property
    def book_similar_books(self):
        if self.similar_books is None:
            self.similar_books = list()
            more_like_this_books = SearchQuerySet().models(Book).more_like_this(self)
            i = 0;
            for book in more_like_this_books:
                if book.object is None:
                    continue
                authors = [a.person_first_name + ' ' + a.person_last_name for a in book.object.book_authors.all()]
                authors = ', ' .join(authors)
                b = RelatedObject(book.object.book_title, book.object.book_lead, book.object.book_image,
                                  book.object.book_date_add, book.object.book_category.publication_category_name, book.object.get_absolute_url(), authors)
                self.similar_books.append(b)
                i = i + 1
                if i >= MAX_NUMBER_OF_SIMILAR_ENTITIES:
                    break
            
        return self.similar_books   

    def __unicode__(self):
        return u'%s' % (self.book_title_text)
     
    def __str__(self):
        return self.book_title_text
     
    def clean(self):
        can_add = True
        if self.book_is_promoted:
            qrs = Book.objects.filter(book_is_promoted=True).exclude(book_id=self.book_id)
            can_add = (qrs.count() < MAX_NUMBER_OF_PROMOTED_ENTITIES);
        if not can_add:
            raise ValidationError(MessageBook.TO_MANY_PROMOTED)
        models.Model.clean(self)
    
    def get_absolute_url(self):
        return "/" + BPORTAL_BASE_URL + "books/%s,%d/details" % (self.book_title_slug, self.book_id)
             
    class Meta:
        ordering = ('book_title_text',)
        verbose_name = FieldBook.VERBOSE_NAME
        verbose_name_plural = FieldBook.VERBOSE_NAME_PLURAL


@reversion.register
class BookFile(models.Model):

    def book_files(self, filename):
        currDate = date.today()
        year = str(currDate.year)
        month = str(currDate.month)
        url = "books/files/%s/%s/%s" % (year, month, filename)
        return url
    
    book = models.ForeignKey(Book, verbose_name=FieldBookFile.BOOK, related_name='book_files')
    file = models.FileField(FieldBookFile.FILE, upload_to=book_files)
    copyright = models.TextField(FieldBookFile.COPYRIGHT, null=True, blank=True)
    
    def __unicode__(self):
        return u'%s' % (basename(self.file.name))
    
    def __str__(self):
        return '%s' % (basename(self.file.name))
    
    class Meta(object):
        verbose_name = FieldBookFile.VERBOSE_NAME
        verbose_name_plural = FieldBookFile.VERBOSE_NAME_PLURAL


@reversion.register 
class BookLink(models.Model):
    book = models.ForeignKey(Book, verbose_name=FieldBookLink.BOOK, related_name='book_links')
    link = models.URLField(FieldBookLink.LINK, null=True, blank=True)
    
    def __unicode__(self):
        return u'%s' % (self.link)
    
    def __str__(self):
        return '%s' % (self.link)
    
    class Meta(object):
        verbose_name = FieldBookLink.VERBOSE_NAME
        verbose_name_plural = FieldBookLink.VERBOSE_NAME_PLURAL


@reversion.register
class BookContentContribution(models.Model):
    book = models.ForeignKey(Book, verbose_name=FieldBookContentContribution.BOOK, related_name='book_content_contributors')
    person = models.ForeignKey(Person, verbose_name=FieldBookContentContribution.PERSON)
    role = models.ForeignKey(PersonContributionRole, verbose_name=FieldBookContentContribution.ROLE)
        
    def __unicode__(self):
        return u'%s %s' % (self.book.book_title_text, self.person.person_last_name)
    
    def __str__(self):
        return '%s %s' % (self.book.book_title_text, self.person.person_last_name)
    
    class Meta(object):
        unique_together = (('book', 'person'),)
        verbose_name = FieldBookContentContribution.VERBOSE_NAME
        verbose_name_plural = FieldBookContentContribution.VERBOSE_NAME_PLURAL


class BookAuthorized(models.Model):
    book = models.ForeignKey(Book, verbose_name=FieldBookAuthorized.BOOK)
    authorized = models.ForeignKey(Institution, verbose_name=FieldBookAuthorized.AUTHORIZED)
        
    def __unicode__(self):
        return u'%s %s' % (self.book.book_title_text, self.authorized.institution_shortname)
    
    def __str__(self):
        return '%s %s' % (self.book.book_title_text, self.authorized.institution_shortname)
    
    class Meta(object):
        unique_together = (('book', 'authorized'),)
        verbose_name = FieldBookAuthorized.VERBOSE_NAME
        verbose_name_plural = FieldBookAuthorized.VERBOSE_NAME_PLURAL 


class BookModification(models.Model):
    book = models.ForeignKey(Book, verbose_name=FieldBookModification.BOOK)
    user = models.ForeignKey(User, verbose_name=FieldBookModification.USER)
    date_time = models.DateTimeField(FieldBookModification.DATE_TIME)
    
    def __unicode__(self):
        return u'%s %s' % (self.book.book_title_text, self.user.username)
    
    def __str__(self):
        return '%s %s' % (self.book.book_title_text, self.user.username)
    
    class Meta(object):
        verbose_name = FieldBookModification.VERBOSE_NAME
        verbose_name_plural = FieldBookModification.VERBOSE_NAME_PLURAL
                
