# -*- coding: utf-8 -*-
from django.core.exceptions import PermissionDenied

from .models import ScholarshipAuthorized


def has_scholarship_write_permission(user, scholarship):
    try:
        if user is None or user.userprofile is None:
            return False
    except AttributeError:
        return False
    if user.is_superuser:
        return True
    if user.userprofile.user_is_editor:
        scholarship_authorized = ScholarshipAuthorized.objects.filter(scholarship=scholarship).select_related('authorized')
        authorized = [sa.authorized for sa in scholarship_authorized]
        resultset = set(authorized) & set(user.userprofile.user_institution.all())
        if resultset:
            return True
    return False

def check_scholarship_write_permission(user, scholarship):
    if has_scholarship_write_permission(user, scholarship):
        return scholarship;
    raise PermissionDenied

def has_scholarship_read_permission(user, scholarship):
    if scholarship.scholarship_is_accepted:
        return True
    return has_scholarship_write_permission(user, scholarship)

def check_scholarship_read_permission(user, scholarship):
    if has_scholarship_read_permission(user, scholarship):
        return scholarship;
    raise PermissionDenied


