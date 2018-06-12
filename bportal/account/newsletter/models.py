# -*- coding: utf-8 -*-
from .fields import FieldNewsletter, FieldManagementEmail
from django.db import models
from bportal.account.profile.models import UserProfile
from django.contrib.sites.models import Site
from bportal.module.event.models import EventCategory
from bportal.module.new.models import NewCategory
from bportal.account.newsletter.fields import FieldNewsletterCustomContent

#newsletter period
NEWSPERIOD_WEEK = 'week'
NEWSPERIOD_TWO_WEEKS = 'two_weeks'
NEWSPERIOD_MONTH = 'month'
NEWSPERIOD_NOT = 'not'

NewsletterPeriod = (
    (NEWSPERIOD_WEEK, 'tygodniowy'),
    (NEWSPERIOD_TWO_WEEKS, 'dwutygodniowy'),
    (NEWSPERIOD_MONTH, 'miesięczny'),
    (NEWSPERIOD_NOT, 'nie chcę otrzymywać'),
)

class NewsletterConfig(models.Model):
    user = models.OneToOneField(UserProfile)
    period = models.CharField(FieldNewsletter.PERIOD, max_length=15, default=NEWSPERIOD_NOT, choices = NewsletterPeriod)
    article = models.BooleanField(FieldNewsletter.ARTICLE, default=False)
    journal = models.BooleanField(FieldNewsletter.JOURNAL, default=False)
    book = models.BooleanField(FieldNewsletter.BOOK, default=False)
    project = models.BooleanField(FieldNewsletter.PROJECT, default=False)
    dissertation = models.BooleanField(FieldNewsletter.DISSERTATION, default=False)
    competition = models.BooleanField(FieldNewsletter.COMPETITION, default=False)
    joboffer = models.BooleanField(FieldNewsletter.JOBOFFER, default=False)
    eduoffer = models.BooleanField(FieldNewsletter.EDUOFFER, default=False)  
    scholarship = models.BooleanField(FieldNewsletter.SCHOLARSHIP, default=False)
    event_categories = models.ManyToManyField(EventCategory, verbose_name=FieldNewsletter.EVENT_CATEGORIES, blank=True, related_name='+')
    new_categories = models.ManyToManyField(NewCategory, verbose_name=FieldNewsletter.NEW_CATEGORIES, blank=True, related_name='+')
    last_sent = models.DateField(FieldNewsletter.LAST_SENT, null=True)
    UUID = models.UUIDField(FieldNewsletter.UUID, null=True, blank=True)
    
    def __unicode__(self):
        return u'%s' % (self.user.user.username)
    
    def __str__(self):
        return self.user.user.username
       
    class Meta:
        verbose_name = FieldNewsletter.VERBOSE_NAME
        verbose_name_plural = FieldNewsletter.VERBOSE_NAME_PLURAL

class NewsletterCustomContent(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.TextField(FieldNewsletterCustomContent.TITLE, null=True, blank=True)
    message = models.TextField(FieldNewsletterCustomContent.MESSAGE)
    valid_since = models.DateField(FieldNewsletterCustomContent.VALID_SINCE, null=True, blank=True)
    valid_until = models.DateField(FieldNewsletterCustomContent.VALID_UNTIL, null=False, blank=False)
    
    def __unicode__(self):
        return u'%s' % (self.title)
    
    def __str__(self):
        return self.title
       
    class Meta:
        ordering = ('-valid_until',)        
        verbose_name = FieldNewsletterCustomContent.VERBOSE_NAME
        verbose_name_plural = FieldNewsletterCustomContent.VERBOSE_NAME_PLURAL

class ManagementEmail(models.Model):
    site = models.OneToOneField(Site)
    title = models.CharField(FieldManagementEmail.TITLE, max_length=500)
    message = models.TextField(FieldManagementEmail.MESSAGE)
    
    def __unicode__(self):
        return u'%s' % (self.title)
    
    def __str__(self):
        return self.title
       
    class Meta:
        verbose_name = FieldManagementEmail.VERBOSE_NAME
        verbose_name_plural = FieldManagementEmail.VERBOSE_NAME_PLURAL
        