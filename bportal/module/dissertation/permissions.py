# -*- coding: utf-8 -*-
from django.core.exceptions import PermissionDenied

from .models import DissertationAuthorized


def has_dissertation_write_permission(user, dissertation):
    try:
        if user is None or user.userprofile is None:
            return False
    except AttributeError:
        return False
    if user.is_superuser:
        return True
    if user.userprofile.user_is_editor:
        dissertation_authorized = DissertationAuthorized.objects.filter(dissertation=dissertation).select_related('authorized')
        authorized = [da.authorized for da in dissertation_authorized]
        resultset = set(authorized) & set(user.userprofile.user_institution.all())
        if resultset:
            return True
    return False

def check_dissertation_write_permission(user, dissertation):
    if has_dissertation_write_permission(user, dissertation):
        return dissertation;
    raise PermissionDenied

def has_dissertation_read_permission(user, dissertation):
    if dissertation.dissertation_is_accepted:
        return True
    return has_dissertation_write_permission(user, dissertation)

def check_dissertation_read_permission(user, dissertation):
    if has_dissertation_read_permission(user, dissertation):
        return dissertation;
    raise PermissionDenied

    