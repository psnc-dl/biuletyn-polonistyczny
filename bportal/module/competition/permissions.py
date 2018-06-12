# -*- coding: utf-8 -*-
from django.core.exceptions import PermissionDenied

from .models import CompetitionAuthorized


def has_competition_write_permission(user, competition):
    try:
        if user is None or user.userprofile is None:
            return False
    except AttributeError:
        return False
    if user.is_superuser:
        return True
    if user.userprofile.user_is_editor:
        competition_authorized = CompetitionAuthorized.objects.filter(competition=competition).select_related('authorized')
        authorized = [ca.authorized for ca in competition_authorized]
        resultset = set(authorized) & set(user.userprofile.user_institution.all())
        if resultset:
            return True
    return False

def check_competition_write_permission(user, competition):
    if has_competition_write_permission(user, competition):
        return competition;
    raise PermissionDenied

def has_competition_read_permission(user, competition):
    if competition.competition_is_accepted:
        return True
    return has_competition_write_permission(user, competition)

def check_competition_read_permission(user, competition):
    if has_competition_read_permission(user, competition):
        return competition;
    raise PermissionDenied

    