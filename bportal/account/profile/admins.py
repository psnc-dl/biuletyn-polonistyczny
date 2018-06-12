# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .fields import FieldUserProfile
from .forms import ProfileAdminForm
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    form = ProfileAdminForm
    can_delete = False

class UserAdmin(UserAdmin):
    inlines = (UserProfileInline, )
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_editor_institutions', 'last_login', 'get_user_last_edit_date_time')
    ordering = ('-last_login', )
    
    def get_editor_institutions(self, obj):
        return [str(institution) for institution in set(obj.userprofile.user_institution.all())]
    get_editor_institutions.short_description = FieldUserProfile.INSTITUTIONS_EDITOR

    def get_user_last_edit_date_time(self, obj):
        return obj.userprofile.user_last_edit_date_time
    get_user_last_edit_date_time.short_description = FieldUserProfile.LAST_EDIT_DATE_TIME
    get_user_last_edit_date_time.admin_order_field = 'userprofile__user_last_edit_date_time'
