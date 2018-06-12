# -*- coding: utf-8 -*-
from django.core.exceptions import PermissionDenied

from .models import EventAuthorized


def has_event_write_permission(user, event):
    try:
        if user is None or user.userprofile is None:
            return False
    except AttributeError:
        return False
    if user.is_superuser:
        return True
    if user.userprofile.user_is_editor:
        event_authorized = EventAuthorized.objects.filter(event=event).select_related('authorized')
        authorized = [ea.authorized for ea in event_authorized]
        resultset = set(authorized) & set(user.userprofile.user_institution.all())
        if resultset:
            return True
    return False

def check_event_write_permission(user, event):
    if has_event_write_permission(user, event):
        return event;
    raise PermissionDenied

def has_event_read_permission(user, event):
    if event.event_is_accepted:
        return True
    return has_event_write_permission(user, event)

def check_event_read_permission(user, event):
    if has_event_read_permission(user, event):
        return event;
    raise PermissionDenied

