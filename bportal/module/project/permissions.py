# -*- coding: utf-8 -*-
from django.core.exceptions import PermissionDenied

from .models import ProjectAuthorized


def has_project_write_permission(user, project):
    try:
        if user is None or user.userprofile is None:
            return False
    except AttributeError:
        return False
    if user.is_superuser:
        return True
    if user.userprofile.user_is_editor:
        project_authorized = ProjectAuthorized.objects.filter(project=project).select_related('authorized')
        authorized = [pa.authorized for pa in project_authorized]
        resultset = set(authorized) & set(user.userprofile.user_institution.all())
        if resultset:
            return True
    return False

def check_project_write_permission(user, project):
    if has_project_write_permission(user, project):
        return project;
    raise PermissionDenied

def has_project_read_permission(user, project):
    if project.project_is_accepted:
        return True
    return has_project_write_permission(user, project)

def check_project_read_permission(user, project):
    if has_project_read_permission(user, project):
        return project;
    raise PermissionDenied


