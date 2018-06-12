# -*- coding: utf-8 -*-
from django.core.exceptions import PermissionDenied

from .models import EducationalOfferAuthorized


def has_eduoffer_write_permission(user, eduoffer):
    try:
        if user is None or user.userprofile is None:
            return False
    except AttributeError:
        return False
    if user.is_superuser:
        return True
    if user.userprofile.user_is_editor:
        eduoffer_authorized = EducationalOfferAuthorized.objects.filter(eduoffer=eduoffer).select_related('authorized')
        authorized = [ea.authorized for ea in eduoffer_authorized]
        resultset = set(authorized) & set(user.userprofile.user_institution.all())
        if resultset:
            return True
    return False

def check_eduoffer_write_permission(user, eduoffer):
    if has_eduoffer_write_permission(user, eduoffer):
        return eduoffer;
    raise PermissionDenied

def has_eduoffer_read_permission(user, eduoffer):
    if eduoffer.eduoffer_is_accepted:
        return True
    return has_eduoffer_write_permission(user, eduoffer)

def check_eduoffer_read_permission(user, eduoffer):
    if has_eduoffer_read_permission(user, eduoffer):
        return eduoffer;
    raise PermissionDenied

    