# -*- coding: utf-8 -*-
from django.core.exceptions import PermissionDenied

from .models import ArticleAuthorized


def has_article_write_permission(user, article):
    try:
        if user is None or user.userprofile is None:
            return False
    except AttributeError:
        return False
    if user.is_superuser:
        return True
    if user.userprofile.user_is_editor:
        article_authorized = ArticleAuthorized.objects.filter(article=article).select_related('authorized')
        authorized = [aa.authorized for aa in article_authorized]
        resultset = set(authorized) & set(user.userprofile.user_institution.all())
        if resultset:
            return True
    return False

def check_article_write_permission(user, article):
    if has_article_write_permission(user, article):
        return article;
    raise PermissionDenied

def has_article_read_permission(user, article):
    if article.article_is_accepted:
        return True
    return has_article_write_permission(user, article)

def check_article_read_permission(user, article):
    if has_article_read_permission(user, article):
        return article;
    raise PermissionDenied
