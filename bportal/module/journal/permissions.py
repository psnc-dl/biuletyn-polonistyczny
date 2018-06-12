# -*- coding: utf-8 -*-
from django.core.exceptions import PermissionDenied

from .models import JournalIssueAuthorized


def has_journalissue_write_permission(user, journalissue):
    try:
        if user is None or user.userprofile is None:
            return False
    except AttributeError:
        return False
    if user.is_superuser:
        return True
    if user.userprofile.user_is_editor:
        journalissue_authorized = JournalIssueAuthorized.objects.filter(journalissue=journalissue).select_related('authorized')
        authorized = [ba.authorized for ba in journalissue_authorized]
        resultset = set(authorized) & set(user.userprofile.user_institution.all())
        if resultset:
            return True
    return False

def check_journalissue_write_permission(user, journalissue):
    if has_journalissue_write_permission(user, journalissue):
        return journalissue;
    raise PermissionDenied

def has_journalissue_read_permission(user, journalissue):
    if journalissue.journalissue_is_accepted:
        return True
    return has_journalissue_write_permission(user, journalissue)

def check_journalissue_read_permission(user, journalissue):
    if has_journalissue_read_permission(user, journalissue):
        return journalissue;
    raise PermissionDenied