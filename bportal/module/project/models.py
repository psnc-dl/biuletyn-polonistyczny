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
from imagekit.models import ImageSpecField
from meta.models import ModelMeta
import reversion
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase

from bportal.module.common.constants import MAX_NUMBER_OF_PROMOTED_ENTITIES, MAX_NUMBER_OF_SIMILAR_ENTITIES
from bportal.module.common.models import TargetGroup, ResearchDiscipline, RelatedObject
from bportal.module.competition.models import Competition
from bportal.module.dissertation.models import Dissertation 
from bportal.module.educationaloffer.models import EducationalOffer
from bportal.module.event.models import Event
from bportal.module.institution.models import Institution, InstitutionRole
from bportal.module.joboffer.models import JobOffer
from bportal.module.person.models import Person, PersonContributionRole
from bportal.module.scholarship.models import Scholarship
from bportal.settings import BPORTAL_BASE_URL

from .fields import FieldProject, FieldProjectParticipant, FieldProjectInstitution, FieldProjectFile, FieldProjectLink, FieldProjectContentContribution, FieldProjectAuthorized, FieldProjectModification
from .messages import MessageProject


class TaggedProject(TaggedItemBase):
    content_object = models.ForeignKey('Project')
    
    def __unicode__(self):
        return u'%s' % (self.tag)
    
    def __str__(self):
        return '%s' % (self.tag)


@reversion.register(exclude=['project_is_promoted'], follow=['project_participants', 'project_institutions', 'project_files', 'project_links', 'project_content_contributors'])
class Project(ModelMeta, models.Model):
    
    def image_file(self, filename):
        currDate = date.today()
        year = str(currDate.year)
        month = str(currDate.month)
        url = "projects/images/%s/%s/%s" % (year, month, filename)
        return url
    
    project_id = models.AutoField(primary_key=True)
    project_title = models.TextField(FieldProject.TITLE)
    project_title_text = models.TextField(FieldProject.TITLE)
    project_title_slug = models.SlugField(unique=False, max_length=128)
    project_lead = models.TextField(FieldProject.LEAD, null=True, blank=False)    
    project_image = models.ImageField(FieldProject.IMAGE, upload_to=image_file, null=True, blank=True)
    project_image_thumbnail = ImageSpecField(source='project_image', format='JPEG', options={'quality': 60})
    project_image_copyright = models.TextField(FieldProject.IMAGE_COPYRIGHT, null=True, blank=True)
    project_image_caption = models.CharField(FieldProject.IMAGE_CAPTION, max_length=1024, null=True, blank=True)
    project_date_start = models.DateField(FieldProject.DATE_START, null=True, blank=True)
    project_date_end = models.DateField(FieldProject.DATE_END, null=True, blank=True)
    project_disciplines = models.ManyToManyField(ResearchDiscipline, verbose_name=FieldProject.DISCIPLINES, blank=True, related_name='discipline_projects+')
    project_targets = models.ManyToManyField(TargetGroup, verbose_name=FieldProject.TARGETS, blank=True, related_name='target_group_projects+')
    project_institutions = models.ManyToManyField(Institution, through='ProjectInstitution', through_fields=('project', 'institution'), verbose_name=FieldProject.INSTITUTIONS, blank=True, related_name='institution_projects')
    project_financing = models.CharField(FieldProject.FINANCING, null=True, blank=True, max_length=1024)
    project_cities = models.ManyToManyField(City, verbose_name=FieldProject.CITIES, related_name='city_projects+', blank=True)
    project_participants = models.ManyToManyField(Person, through='ProjectParticipant', through_fields=('project', 'person'), verbose_name=FieldProject.PARTICIPANTS, blank=True, related_name='person_projects')
    project_contact = models.CharField(FieldProject.CONTACT, null=True, blank=True, max_length=1024)
    project_description = models.TextField(FieldProject.DESCRIPTION, null=False, blank=False)
    project_support = models.CharField(FieldProject.SUPPORT, null=True, blank=True, max_length=1024)
    project_date_add = models.DateTimeField(FieldProject.DATE_ADD, default=timezone.now)
    project_date_edit = models.DateTimeField(FieldProject.DATE_EDIT, default=timezone.now)
    project_keywords = TaggableManager(verbose_name=FieldProject.KEYWORDS, through=TaggedProject)
    project_connected_events = models.ManyToManyField(Event, verbose_name=FieldProject.CONNECTED_EVENTS, blank=True, related_name='event_connected_projects')
    project_connected_dissertations = models.ManyToManyField(Dissertation, verbose_name=FieldProject.CONNECTED_DISSERTATIONS, blank=True, related_name='dissertation_connected_projects')    
    project_connected_competitions = models.ManyToManyField(Competition, verbose_name=FieldProject.CONNECTED_COMPETITIONS, blank=True, related_name='competition_connected_projects')
    project_connected_joboffers = models.ManyToManyField(JobOffer, verbose_name=FieldProject.CONNECTED_JOBOFFERS, blank=True, related_name='joboffer_connected_projects')    
    project_connected_eduoffers = models.ManyToManyField(EducationalOffer, verbose_name=FieldProject.CONNECTED_EDUOFFERS, blank=True, related_name='eduoffer_connected_projects')    
    project_connected_scholarships = models.ManyToManyField(Scholarship, verbose_name=FieldProject.CONNECTED_SCHOLARSHIPS, blank=True, related_name='scholarship_connected_projects')    
    project_added_by = models.ForeignKey(User, verbose_name=FieldProject.ADDED_BY, null=True, blank=True, related_name='user_added_projects')
    project_modified_by = models.ForeignKey(User, verbose_name=FieldProject.MODIFIED_BY, null=True, blank=True, related_name='user_modified_projects')
    project_is_accepted = models.BooleanField(FieldProject.IS_ACCEPTED, default=False)
    project_is_promoted = models.BooleanField(FieldProject.IS_PROMOTED, default=False)
    project_opi_id = models.IntegerField(FieldProject.OPI_ID, null=True, blank=True)
    project_authorizations = models.ManyToManyField(Institution, through='ProjectAuthorized', through_fields=('project', 'authorized'), blank=True, related_name='authorization_projects+')
    
    curr_page = None
    per_page = None
    filter = None
    related_objects = None
    similar_projects = None
    
    #import
    is_imported = False
    
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
        return self.project_title_text
        
    def get_meta_description(self):
        if self.project_lead:
            return strip_tags(self.project_lead)

    def get_meta_image(self):
        if self.project_image:
            return self.build_absolute_uri(self.project_image.url)
        
    def project_title_safe(self):
        return mark_safe(self.project_title)    
    
    @property
    def project_related_objects(self):
        if self.related_objects is None:
            self.related_objects = list()
            for c in self.project_connected_competitions.all().order_by('competition_date_add'):
                r = RelatedObject(c.competition_title, c.competition_lead, c.competition_image, c.competition_date_add, 'competition',
                                  c.get_absolute_url())
                self.related_objects.append(r)
            for d in self.project_connected_dissertations.all().order_by('dissertation_date_add'):
                r = RelatedObject(d.dissertation_title, d.dissertation_lead, d.dissertation_image, d.dissertation_date_add, 'dissertation',
                                  d.get_absolute_url())
                self.related_objects.append(r)
            for eo in self.project_connected_eduoffers.all().order_by('eduoffer_date_add'):
                r = RelatedObject(eo.eduoffer_position, eo.eduoffer_lead, eo.eduoffer_image, eo.eduoffer_date_add, 'eduoffer',
                                  eo.get_absolute_url())
                self.related_objects.append(r)
            for e in self.project_connected_events.all().order_by('event_date_add'):
                r = RelatedObject(e.event_name, e.event_lead, e.event_poster, e.event_date_add, 'event',
                                  e.get_absolute_url())
                self.related_objects.append(r)
            for jo in self.project_connected_joboffers.all().order_by('joboffer_date_add'):
                r = RelatedObject(jo.joboffer_position, jo.joboffer_lead, jo.joboffer_image, jo.joboffer_date_add, 'joboffer',
                                  jo.get_absolute_url())
                self.related_objects.append(r)
            for s in self.project_connected_scholarships.all().order_by('scholarship_date_add'):
                r = RelatedObject(s.scholarship_name, s.scholarship_lead, s.scholarship_image, s.scholarship_date_add, 'scholarship',
                                  s.get_absolute_url())
                self.related_objects.append(r)
            
            self.related_objects.sort(key=lambda ro : ro.date_add, reverse=True)
            
        return self.related_objects

    @property
    def project_similar_projects(self):
        if self.similar_projects is None:
            self.similar_projects = list()
            more_like_this_projects = SearchQuerySet().models(Project).more_like_this(self)
            i = 0;
            for project in more_like_this_projects:
                if project.object is None:
                    continue
                p = RelatedObject(project.object.project_title, project.object.project_lead, project.object.project_image,
                                  project.object.project_date_add, None, project.object.get_absolute_url())
                self.similar_projects.append(p)
                i = i + 1
                if i >= MAX_NUMBER_OF_SIMILAR_ENTITIES:
                    break
            
        return self.similar_projects

    def __unicode__(self):
        return u'%s' % (self.project_title_text)
    
    def __str__(self):
        if self.project_title_text is not None:
            return self.project_title_text
        else:
            return ''
    
    def clean(self):
        can_add = True
        if self.project_is_promoted:
            qrs = Project.objects.filter(project_is_promoted=True).exclude(project_id=self.project_id)
            can_add = (qrs.count() < MAX_NUMBER_OF_PROMOTED_ENTITIES);
        if not can_add:
            raise ValidationError(MessageProject.TO_MANY_PROMOTED)
        models.Model.clean(self)
        
    def get_absolute_url(self):
        return "/" + BPORTAL_BASE_URL + "projects/%s,%d/details" % (self.project_title_slug, self.project_id)
        
    class Meta:
        ordering = ('project_title_text',)
        verbose_name = FieldProject.VERBOSE_NAME
        verbose_name_plural = FieldProject.VERBOSE_NAME_PLURAL


@reversion.register
class ProjectParticipant(models.Model):
    project = models.ForeignKey(Project, verbose_name=FieldProjectParticipant.PROJECT, related_name='project_person_participations')
    person = models.ForeignKey(Person, verbose_name=FieldProjectParticipant.PERSON)
    is_principal = models.BooleanField(verbose_name=FieldProjectParticipant.IS_PRINCIPAL, default=False)
    
    def __unicode__(self):
        return u'%s %s' % (self.project.project_title_text, self.person.person_last_name)
    
    def __str__(self):
        return '%s %s' % (self.project.project_title_text, self.person.person_last_name)
    
    class Meta(object):
        verbose_name = FieldProjectParticipant.VERBOSE_NAME
        verbose_name_plural = FieldProjectParticipant.VERBOSE_NAME_PLURAL


@reversion.register
class ProjectInstitution(models.Model):
    project = models.ForeignKey(Project, verbose_name=FieldProjectInstitution.PROJECT, related_name='project_institution_participations')
    institution = models.ForeignKey(Institution, verbose_name=FieldProjectInstitution.INSTITUTION)
    role = models.ForeignKey(InstitutionRole, verbose_name=FieldProjectInstitution.ROLE)
        
    def __unicode__(self):
        return u'%s %s' % (self.project.project_title_text, self.institution.institution_shortname)
    
    def __str__(self):
        return '%s %s' % (self.project.project_title_text, self.institution.institution_shortname)
    
    class Meta(object):
        unique_together = (('project', 'institution'),)
        verbose_name = FieldProjectInstitution.VERBOSE_NAME
        verbose_name_plural = FieldProjectInstitution.VERBOSE_NAME_PLURAL
  

@reversion.register
class ProjectFile(models.Model):

    def project_files(self, filename):
        currDate = date.today()
        year = str(currDate.year)
        month = str(currDate.month)
        url = "projects/files/%s/%s/%s" % (year, month, filename)
        return url
    
    project = models.ForeignKey(Project, verbose_name=FieldProjectFile.PROJECT, related_name='project_files')
    file = models.FileField(FieldProjectFile.FILE, upload_to=project_files)
    copyright = models.TextField(FieldProjectFile.COPYRIGHT, null=True, blank=True)
    
    def __unicode__(self):
        return u'%s' % (basename(self.file.name))
    
    def __str__(self):
        return '%s' % (basename(self.file.name))
    
    class Meta(object):
        verbose_name = FieldProjectFile.VERBOSE_NAME
        verbose_name_plural = FieldProjectFile.VERBOSE_NAME_PLURAL


@reversion.register 
class ProjectLink(models.Model):
    project = models.ForeignKey(Project, verbose_name=FieldProjectLink.PROJECT, related_name='project_links')
    link = models.URLField(FieldProjectLink.LINK, null=True, blank=True)
    
    def __unicode__(self):
        return u'%s' % (self.link)
    
    def __str__(self):
        return '%s' % (self.link)
    
    class Meta(object):
        verbose_name = FieldProjectLink.VERBOSE_NAME
        verbose_name_plural = FieldProjectLink.VERBOSE_NAME_PLURAL


@reversion.register 
class ProjectContentContribution(models.Model):
    project = models.ForeignKey(Project, verbose_name=FieldProjectContentContribution.PROJECT, related_name='project_content_contributors')
    person = models.ForeignKey(Person, verbose_name=FieldProjectContentContribution.PERSON)
    role = models.ForeignKey(PersonContributionRole, verbose_name=FieldProjectContentContribution.ROLE)
        
    def __unicode__(self):
        return u'%s %s' % (self.project.project_title_text, self.person.person_last_name)
    
    def __str__(self):
        return '%s %s' % (self.project.project_title_text, self.person.person_last_name)
    
    class Meta(object):
        unique_together = (('project', 'person'),)
        verbose_name = FieldProjectContentContribution.VERBOSE_NAME
        verbose_name_plural = FieldProjectContentContribution.VERBOSE_NAME_PLURAL


class ProjectAuthorized(models.Model):
    project = models.ForeignKey(Project, verbose_name=FieldProjectAuthorized.PROJECT)
    authorized = models.ForeignKey(Institution, verbose_name=FieldProjectAuthorized.AUTHORIZED)
        
    def __unicode__(self):
        return u'%s %s' % (self.project.project_title_text, self.authorized.institution_shortname)
    
    def __str__(self):
        return '%s %s' % (self.project.project_title_text, self.authorized.institution_shortname)
    
    class Meta(object):
        unique_together = (('project', 'authorized'),)
        verbose_name = FieldProjectAuthorized.VERBOSE_NAME
        verbose_name_plural = FieldProjectAuthorized.VERBOSE_NAME_PLURAL


class ProjectModification(models.Model):
    project = models.ForeignKey(Project, verbose_name=FieldProjectModification.PROJECT)
    user = models.ForeignKey(User, verbose_name=FieldProjectModification.USER)
    date_time = models.DateTimeField(FieldProjectModification.DATE_TIME)
    
    def __unicode__(self):
        return u'%s %s' % (self.project.project_title_text, self.user.username)
    
    def __str__(self):
        return '%s %s' % (self.project.project_title_text, self.user.username)
    
    class Meta(object):
        verbose_name = FieldProjectModification.VERBOSE_NAME
        verbose_name_plural = FieldProjectModification.VERBOSE_NAME_PLURAL

