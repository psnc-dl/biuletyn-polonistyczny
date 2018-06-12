# -*- coding: utf-8 -*-
from django.core.exceptions import PermissionDenied

from .models import BookAuthorized


def has_book_write_permission(user, book):
    try:
        if user is None or user.userprofile is None:
            return False
    except AttributeError:
        return False
    if user.is_superuser:
        return True
    if user.userprofile.user_is_editor:
        book_authorized = BookAuthorized.objects.filter(book=book).select_related('authorized')
        authorized = [ba.authorized for ba in book_authorized]
        resultset = set(authorized) & set(user.userprofile.user_institution.all())
        if resultset:
            return True
    return False

def check_book_write_permission(user, book):
    if has_book_write_permission(user, book):
        return book;
    raise PermissionDenied

def has_book_read_permission(user, book):
    if book.book_is_accepted:
        return True
    return has_book_write_permission(user, book)

def check_book_read_permission(user, book):
    if has_book_read_permission(user, book):
        return book;
    raise PermissionDenied

    