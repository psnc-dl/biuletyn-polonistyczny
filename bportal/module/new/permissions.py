# -*- coding: utf-8 -*-
from django.core.exceptions import PermissionDenied

from .models import NewAuthorized


def has_new_write_permission(user, new):
    try:
        if user is None or user.userprofile is None:
            return False
    except AttributeError:
        return False
    if user.is_superuser:
        return True
    if user.userprofile.user_is_editor:
        new_authorized = NewAuthorized.objects.filter(new=new).select_related('authorized')
        authorized = [na.authorized for na in new_authorized]
        resultset = set(authorized) & set(user.userprofile.user_institution.all())
        if resultset:
            return True
    return False

def check_new_write_permission(user, new):
    if has_new_write_permission(user, new):
        return new;
    raise PermissionDenied

def has_new_read_permission(user, new):
    if new.new_is_accepted:
        return True
    return has_new_write_permission(user, new)

def check_new_read_permission(user, new):
    if has_new_read_permission(user, new):
        return new;
    raise PermissionDenied
