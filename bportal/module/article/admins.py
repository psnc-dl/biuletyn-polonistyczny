# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils import timezone
from django.utils.html import strip_tags
from reversion.admin import VersionAdmin

from bportal.account.profile.models import UserProfile
from bportal.module.common.utils import remove_unnecessary_tags_from_title, slugify_text_title

from .forms import ArticleAdminForm, ArticleConfirmAdminForm, ArticleFileForm, ArticleLinkForm, ArticleContentContributionAdminForm
from .models import ArticleFile, ArticleLink, ArticleContentContribution, ArticleAuthorized, ArticleModification


class ArticleFileAdminInline(admin.TabularInline):
    model = ArticleFile
    form = ArticleFileForm
    extra = 1


class ArticleLinkAdminInline(admin.TabularInline):
    model = ArticleLink
    form = ArticleLinkForm
    extra = 1


class ArticleContentContributionAdminInline(admin.TabularInline):
    model = ArticleContentContribution
    form = ArticleContentContributionAdminForm
    extra = 1    
    
class ArticleAdmin(VersionAdmin):
    list_display = ('article_title_safe', 'article_date_add', 'article_added_by', 'article_date_edit', 'article_modified_by',)
    inlines = (ArticleFileAdminInline, ArticleLinkAdminInline, ArticleContentContributionAdminInline)
    form = ArticleAdminForm
    search_fields = ('article_title_text',)
    list_filter = ('article_is_accepted', 'article_is_promoted')    
    
    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.form = ArticleAdminForm
        else:
            self.form = ArticleConfirmAdminForm
        return super(ArticleAdmin, self).get_form(request, obj, **kwargs)
   
    def save_model(self, request, obj, form, change):
        if obj.article_added_by is None:
            obj.article_added_by = request.user
        obj.article_modified_by = request.user
        obj.article_title = remove_unnecessary_tags_from_title(obj.article_title)
        obj.article_title_text = strip_tags(obj.article_title)
        obj.article_title_slug = slugify_text_title(obj.article_title_text)           
                  
        super(VersionAdmin, self).save_model(request, obj, form, change)
          
        modification = ArticleModification.objects.create(article=obj, user=request.user, date_time=timezone.now())
          
        profile = UserProfile.objects.get(user=request.user)
        authorized = ArticleAuthorized.objects.filter(article=obj);
        if not authorized.exists() :
            institutions = profile.user_institution.all()
            for institution in institutions:
                ArticleAuthorized.objects.create(article=obj, authorized=institution)
        profile.user_last_edit_date_time = modification.date_time
        profile.save() 
