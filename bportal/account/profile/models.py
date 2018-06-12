# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from bportal.module.common.constants import DEFAULT_PER_PAGE
from bportal.module.institution.models import Institution
from bportal.module.person.models import Person

from .fields import FieldUserProfile


class UserProfile(models.Model):
    
    def image_file(self, filename):
        url = "users/images/%s" % (filename)
        return url

    user = models.OneToOneField(User, related_name='userprofile')
    user_institution = models.ManyToManyField(Institution, verbose_name=FieldUserProfile.INSTITUTION, blank=True, related_name='institution_editors')
    user_is_editor = models.BooleanField(FieldUserProfile.IS_EDITOR, blank=True, default=False)
    user_photo = models.ImageField(FieldUserProfile.PHOTO, null=True, blank=True, upload_to=image_file)
    user_nick = models.CharField(FieldUserProfile.NICK, max_length=30, blank=True)
    user_born_date = models.DateField(FieldUserProfile.BORN_DATE, null=True, blank=True)
    user_phone = PhoneNumberField(FieldUserProfile.PHONE, null=True, blank=True)
    user_person = models.OneToOneField(Person, verbose_name=FieldUserProfile.PERSON, null=True, blank=False, related_name='person_user')
    user_items_per_page = models.PositiveSmallIntegerField(FieldUserProfile.ITEMS_PER_PAGE, blank=True, default=DEFAULT_PER_PAGE)
    user_newsletter_flag = models.BooleanField(FieldUserProfile.USER_NEWSLETTER_FLAG, blank=True, default=False)
    user_last_edit_date_time = models.DateTimeField(FieldUserProfile.LAST_EDIT_DATE_TIME, null=True, blank=True)
    UUID = models.UUIDField(FieldUserProfile.UUID, null = True, blank = True)
    
    
    def __unicode__(self):
        return u'%s' % (self.user.username)
    
    def __str__(self):
        return self.user.username
       
    class Meta:
        verbose_name = FieldUserProfile.VERBOSE_NAME
        verbose_name_plural = FieldUserProfile.VERBOSE_NAME_PLURAL
        