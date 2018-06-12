# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils import timezone
from django.utils.html import strip_tags
from reversion.admin import VersionAdmin

from bportal.account.profile.models import UserProfile
from bportal.module.common.utils import remove_unnecessary_tags_from_title, slugify_text_title

from .forms import BookAdminForm, BookConfirmAdminForm, BookFileForm, BookLinkForm, BookContentContributionAdminForm
from .models import BookFile, BookLink, BookContentContribution, BookAuthorized, BookModification

class BookFileAdminInline(admin.TabularInline):
    model = BookFile
    form = BookFileForm
    extra = 1


class BookLinkAdminInline(admin.TabularInline):
    model = BookLink
    form = BookLinkForm
    extra = 1


class BookContentContributionAdminInline(admin.TabularInline):
    model = BookContentContribution
    form = BookContentContributionAdminForm
    extra = 1    

         
class BookAdmin(VersionAdmin):
    list_display = ('book_title_safe', 'book_date_add', 'book_added_by', 'book_date_edit', 'book_modified_by',)
    inlines = (BookFileAdminInline, BookLinkAdminInline, BookContentContributionAdminInline)
    form = BookAdminForm
    search_fields = ('book_title_text',)
    list_filter = ('book_is_accepted', 'book_is_promoted')    

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.form = BookAdminForm
        else:
            self.form = BookConfirmAdminForm
        return super(BookAdmin, self).get_form(request, obj, **kwargs)
    
    def save_model(self, request, obj, form, change):
        if obj.book_added_by is None:
            obj.book_added_by = request.user
        obj.book_modified_by = request.user
        obj.book_title = remove_unnecessary_tags_from_title(obj.book_title)
        obj.book_title_text = strip_tags(obj.book_title)          
        obj.book_title_slug = slugify_text_title(obj.book_title_text)
                  
        super(VersionAdmin, self).save_model(request, obj, form, change)
          
        modification = BookModification.objects.create(book=obj, user=request.user, date_time=timezone.now())
          
        profile = UserProfile.objects.get(user=request.user)
        authorized = BookAuthorized.objects.filter(book=obj);
        if not authorized.exists() :
            institutions = profile.user_institution.all()
            for institution in institutions:
                BookAuthorized.objects.create(book=obj, authorized=institution)
        profile.user_last_edit_date_time = modification.date_time
        profile.save()
