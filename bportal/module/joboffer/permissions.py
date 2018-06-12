# -*- coding: utf-8 -*-
from django.core.exceptions import PermissionDenied

from .models import JobOfferAuthorized


def has_joboffer_write_permission(user, joboffer):
    try:
        if user is None or user.userprofile is None:
            return False
    except AttributeError:
        return False
    if user.is_superuser:
        return True
    if user.userprofile.user_is_editor:
        joboffer_authorized = JobOfferAuthorized.objects.filter(joboffer=joboffer).select_related('authorized')
        authorized = [ja.authorized for ja in joboffer_authorized]
        resultset = set(authorized) & set(user.userprofile.user_institution.all())
        if resultset:
            return True
    return False

def check_joboffer_write_permission(user, joboffer):
    if has_joboffer_write_permission(user, joboffer):
        return joboffer;
    raise PermissionDenied

def has_joboffer_read_permission(user, joboffer):
    if joboffer.joboffer_is_accepted:
        return True
    return has_joboffer_write_permission(user, joboffer)

def check_joboffer_read_permission(user, joboffer):
    if has_joboffer_read_permission(user, joboffer):
        return joboffer;
    raise PermissionDenied




                