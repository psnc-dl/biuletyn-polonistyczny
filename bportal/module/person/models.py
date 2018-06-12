  # -*- coding: utf-8 -*-
from django.db import models
import reversion

from bportal.module.common.models import ResearchDiscipline
from bportal.module.institution.models import Institution
from bportal.settings import BPORTAL_BASE_URL

from .fields import FieldPerson, FieldScientificTitle, FieldPersonAffiliation, FieldPersonContributionRole


class ScientificTitle(models.Model): 
    scientific_title_id = models.AutoField(primary_key=True)
    scientific_title_abbreviation = models.CharField(FieldScientificTitle.ABBREVIATION, max_length=32)
    scientific_title_name = models.CharField(FieldScientificTitle.NAME, max_length=256)
 
    def __unicode__(self):
        return u'%s' % (self.scientific_title_abbreviation)
    
    def __str__(self):
        return self.scientific_title_abbreviation
    
    class Meta:
        ordering = ('scientific_title_abbreviation',)
        verbose_name = FieldScientificTitle.VERBOSE_NAME
        verbose_name_plural = FieldScientificTitle.VERBOSE_NAME_PLURAL

@reversion.register(follow=['person_affiliations',])
class Person(models.Model):
    
    def photo_file(self, filename):
        url = "people/images/%s" % (filename)
        return url
    
    person_id = models.AutoField(primary_key=True)
    person_first_name = models.CharField(FieldPerson.FIRTS_NAME, max_length=256)
    person_last_name = models.CharField(FieldPerson.LAST_NAME, max_length=256)
    person_slug = models.SlugField(unique=False, max_length=128)     
    person_title = models.ForeignKey(ScientificTitle, verbose_name=FieldPerson.TITLE, null=True, blank=True, related_name='+')
    person_institutions = models.ManyToManyField(Institution, through='PersonAffiliation', through_fields=('person', 'institution'), blank=True, related_name='institution_people')
    person_opi_id = models.IntegerField(FieldPerson.OPI_ID, null=True, blank=True)
    person_email = models.CharField(FieldPerson.EMAIL, max_length=256, null=True, blank=True)
    person_photo = models.ImageField(FieldPerson.PHOTO, null=True, blank=True, upload_to=photo_file)
    person_biogram = models.TextField(FieldPerson.BIOGRAM, null=True, blank=True)
    person_disciplines = models.ManyToManyField(ResearchDiscipline, verbose_name=FieldPerson.DISCIPLINES, blank=True, related_name='discipline_people+')
    
    #import
    is_imported = False
    
    def __unicode__(self):
        if (self.person_opi_id is None):
            return u'%s %s' % (self.person_first_name, self.person_last_name)
        else:
            return u'%s %s (OPI ID: %d)' % (self.person_first_name, self.person_last_name, self.person_opi_id)
    
    def __str__(self):
        if (self.person_opi_id is None):
            return '%s %s' % (self.person_first_name, self.person_last_name)
        else:
            return '%s %s (OPI ID: %d)' % (self.person_first_name, self.person_last_name, self.person_opi_id)

    def get_absolute_url(self):
        return "/" + BPORTAL_BASE_URL + "people/%s,%d/details" % (self.person_slug, self.person_id) 
        
    class Meta:
        ordering = ('person_last_name',)
        verbose_name = FieldPerson.VERBOSE_NAME
        verbose_name_plural = FieldPerson.VERBOSE_NAME_PLURAL


@reversion.register
class PersonAffiliation(models.Model):
    person = models.ForeignKey(Person, verbose_name=FieldPersonAffiliation.PERSON, related_name='person_affiliations')
    institution = models.ForeignKey(Institution, verbose_name=FieldPersonAffiliation.INSTITUTION)
    is_principal = models.BooleanField(verbose_name=FieldPersonAffiliation.IS_PRINCIPAL, default=False)
    
    def __unicode__(self):
        return u'%s %s' % (self.person.person_last_name, self.institution.institution_shortname)
    
    def __str__(self):
        return '%s %s' % (self.person.person_last_name, self.institution.institution_shortname)
    
    class Meta(object):      
        verbose_name = FieldPersonAffiliation.VERBOSE_NAME
        verbose_name_plural = FieldPersonAffiliation.VERBOSE_NAME_PLURAL


class PersonContributionRole(models.Model):
    contribution_role_id = models.AutoField(primary_key=True)
    contribution_role_role = models.CharField(FieldPersonContributionRole.ROLE, max_length=64)
    
    def __unicode__(self):
        return u'%s' % (self.contribution_role_role)
    
    def __str__(self):
        return self.contribution_role_role
    
    class Meta:
        verbose_name = FieldPersonContributionRole.VERBOSE_NAME
        verbose_name_plural = FieldPersonContributionRole.VERBOSE_NAME_PLURAL
