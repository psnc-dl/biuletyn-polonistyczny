# -*- coding: utf-8 -*-

def has_create_permission(user):
    try:
        if user is None or user.userprofile is None:
            return False
    except AttributeError:
        return False
    if user.is_superuser or user.userprofile.user_is_editor:
        if user.userprofile.user_institution.all():
            return True
    return False
