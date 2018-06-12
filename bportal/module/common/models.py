# -*- coding: utf-8 -*-
from django.db import models

from bportal.module.common.utils import RelatedObjectHelper

from .fields import FieldTargetGroup, FieldResearchDiscipline, FieldPublicationCategory


class TargetGroup(models.Model):
    target_id = models.AutoField(primary_key=True)
    target_name = models.CharField(FieldTargetGroup.NAME, max_length=256)
    position = models.IntegerField(FieldTargetGroup.POSITION, null=True)
    
    # # necessary in serializing events to JSON    
    def natural_key(self):
        return (self.target_name)
    
    def __unicode__(self):
        return u'%s' % (self.target_name)
    
    def __str__(self):
        return self.target_name
    
    class Meta:
        ordering = ('position',)
        verbose_name = FieldTargetGroup.VERBOSE_NAME
        verbose_name_plural = FieldTargetGroup.VERBOSE_NAME_PLURAL
        

class ResearchDiscipline(models.Model):
    discipline_id = models.AutoField(primary_key=True)
    discipline_fullname = models.CharField(FieldResearchDiscipline.FULLNAME, max_length=2048)
    
    def __unicode__(self):
        return u'%s' % (self.discipline_fullname)
    
    def __str__(self):
        return self.discipline_fullname
       
    class Meta:
        ordering = ('discipline_fullname',)
        verbose_name = FieldResearchDiscipline.VERBOSE_NAME
        verbose_name_plural = FieldResearchDiscipline.VERBOSE_NAME_PLURAL


class PublicationCategory(models.Model):
    publication_category_id = models.AutoField(primary_key=True)
    publication_category_name = models.CharField(FieldPublicationCategory.NAME, max_length=512)

    def __unicode__(self):
        return u'%s' % (self.publication_category_name)
    
    def __str__(self):
        return self.publication_category_name
           
    class Meta:
        ordering = ('publication_category_name',)
        verbose_name = FieldPublicationCategory.VERBOSE_NAME
        verbose_name_plural = FieldPublicationCategory.VERBOSE_NAME_PLURAL        


# related and similar objects
class RelatedObject(models.Model):
    def __init__(self, title=None, lead=None, photo=None, date_add=None, category=None, url=None, prelead=None):
        self.__title = title
        self.__lead = lead
        self.__photo = photo
        self.__date_add = date_add
        self.__category = RelatedObjectHelper.get_category(category)
        self.__url = url
        self.__prelead = prelead
        
    @property
    def title(self):
        return self.__title
    
    @property
    def lead(self):
        return self.__lead
    
    @property
    def photo(self):
        return self.__photo
    
    @property
    def date_add(self):
        return self.__date_add
    
    @property
    def category(self):
        return self.__category
    
    @property
    def url(self):
        return self.__url
    
    @property
    def prelead(self):
        return self.__prelead
    
    class Meta:
        abstract = True
