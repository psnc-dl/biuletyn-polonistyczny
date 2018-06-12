# -*- coding: utf-8 -*-
from cities_light.models import City
from django.db import models
import reversion

from bportal.settings import BPORTAL_BASE_URL

from .fields import FieldInstitutionType, FieldInstitution, FieldInstitutionRole


class InstitutionType(models.Model):
    type_id = models.AutoField(primary_key=True)
    type_name = models.CharField(FieldInstitutionType.NAME, max_length=128)
     
    def __unicode__(self):
        return u'%s' % (self.type_name)

    def __str__(self):
        return self.type_name
     
    class Meta:
        verbose_name = FieldInstitutionType.VERBOSE_NAME
        verbose_name_plural = FieldInstitutionType.VERBOSE_NAME_PLURAL


@reversion.register
class Institution(models.Model):
    
    def image_file(self, filename):
        url = "institutions/images/%s" % (filename)
        return url
    
    institution_id = models.AutoField(primary_key=True)
    institution_shortname = models.CharField(FieldInstitution.SHORTNAME, max_length=32)
    institution_fullname = models.CharField(FieldInstitution.FULLNAME, max_length=1024)    
    institution_slug = models.SlugField(unique=False, max_length=32)    
    institution_type = models.ForeignKey(InstitutionType, verbose_name=FieldInstitution.TYPE, null=True, blank=True)    
    institution_city = models.ForeignKey(City, verbose_name=FieldInstitution.CITY, null=True, blank=True)
    institution_photo = models.ImageField(FieldInstitution.PHOTO, null=True, blank=True, upload_to=image_file)
    institution_www = models.URLField(FieldInstitution.WWW, null=True, blank=True)
    institution_description = models.TextField(FieldInstitution.DESCRIPTION, null=True, blank=True)
    institution_parent = models.ForeignKey('self', related_name="institution_children", null=True, blank=True, verbose_name=FieldInstitution.PARENT)
    
    def __unicode__(self):
        institution_name = self.institution_fullname
        if (self.institution_parent is not None):
            institution_name += " " + self.institution_parent.institution_shortname
        return u'%s' % (institution_name)
    
    def __str__(self):
        institution_name = self.institution_fullname
        if (self.institution_parent is not None):
            institution_name += " " + self.institution_parent.institution_shortname
        return institution_name
    
    @property
    def get_as_dict_key(self):
        institution_name = self.institution_fullname
        if (self.institution_parent is not None):
            institution_name += self.institution_parent.institution_shortname
        return institution_name
        
    def get_absolute_url(self):
        return "/" + BPORTAL_BASE_URL + "institutions/%s,%d/details" % (self.institution_slug, self.institution_id)
          
    class Meta:
        ordering = ('institution_fullname',)
        verbose_name = FieldInstitution.VERBOSE_NAME
        verbose_name_plural = FieldInstitution.VERBOSE_NAME_PLURAL


class InstitutionRole(models.Model):
    institution_role_id = models.AutoField(primary_key=True)
    institution_role_role = models.CharField(FieldInstitutionRole.ROLE, max_length=64)
    
    def __unicode__(self):
        return u'%s' % (self.institution_role_role)
    
    def __str__(self):
        return self.institution_role_role
    
    class Meta:
        verbose_name = FieldInstitutionRole.VERBOSE_NAME
        verbose_name_plural = FieldInstitutionRole.VERBOSE_NAME_PLURAL

