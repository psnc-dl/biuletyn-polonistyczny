from django import template

from bportal.module.article.permissions import has_article_write_permission, has_article_read_permission
from bportal.module.book.permissions import has_book_write_permission, has_book_read_permission
from bportal.module.competition.permissions import has_competition_write_permission, has_competition_read_permission
from bportal.module.dissertation.permissions import has_dissertation_write_permission, has_dissertation_read_permission
from bportal.module.educationaloffer.permissions import has_eduoffer_write_permission, has_eduoffer_read_permission
from bportal.module.event.permissions import has_event_write_permission, has_event_read_permission
from bportal.module.joboffer.permissions import has_joboffer_write_permission, has_joboffer_read_permission
from bportal.module.journal.permissions import has_journalissue_write_permission, has_journalissue_read_permission
from bportal.module.new.permissions import has_new_write_permission, has_new_read_permission
from bportal.module.project.permissions import has_project_write_permission, has_project_read_permission
from bportal.module.scholarship.permissions import has_scholarship_write_permission, has_scholarship_read_permission


register = template.Library()

@register.filter(name='check_event_write_permission')
@register.assignment_tag
def check_event_write_permission(user, event):
    return has_event_write_permission(user, event)

@register.filter(name='check_event_read_permission')
@register.assignment_tag
def check_event_read_permission(user, event):
    return has_event_read_permission(user, event)


@register.filter(name='check_new_write_permission')
@register.assignment_tag
def check_new_write_permission(user, event):
    return has_new_write_permission(user, event)

@register.filter(name='check_new_read_permission')
@register.assignment_tag
def check_new_read_permission(user, event):
    return has_new_read_permission(user, event)


@register.filter(name='check_project_write_permission')
@register.assignment_tag
def check_project_write_permission(user, project):
    return has_project_write_permission(user, project)

@register.filter(name='check_project_read_permission')
@register.assignment_tag
def check_project_read_permission(user, project):
    return has_project_read_permission(user, project)


@register.filter(name='check_dissertation_write_permission')
@register.assignment_tag
def check_dissertation_write_permission(user, dissertation):
    return has_dissertation_write_permission(user, dissertation)

@register.filter(name='check_dissertation_read_permission')
@register.assignment_tag
def check_dissertation_read_permission(user, dissertation):
    return has_dissertation_read_permission(user, dissertation)


@register.filter(name='check_competition_write_permission')
@register.assignment_tag
def check_competition_write_permission(user, competition):
    return has_competition_write_permission(user, competition)

@register.filter(name='check_competition_read_permission')
@register.assignment_tag
def check_competition_read_permission(user, competition):
    return has_competition_read_permission(user, competition)


@register.filter(name='check_joboffer_write_permission')
@register.assignment_tag
def check_joboffer_write_permission(user, joboffer):
    return has_joboffer_write_permission(user, joboffer)

@register.filter(name='check_joboffer_read_permission')
@register.assignment_tag
def check_joboffer_read_permission(user, joboffer):
    return has_joboffer_read_permission(user, joboffer)


@register.filter(name='check_scholarship_write_permission')
@register.assignment_tag
def check_scholarship_write_permission(user, scholarship):
    return has_scholarship_write_permission(user, scholarship)

@register.filter(name='check_scholarship_read_permission')
@register.assignment_tag
def check_scholarship_read_permission(user, scholarship):
    return has_scholarship_read_permission(user, scholarship)


@register.filter(name='check_eduoffer_write_permission')
@register.assignment_tag
def check_eduoffer_write_permission(user, eduoffer):
    return has_eduoffer_write_permission(user, eduoffer)

@register.filter(name='check_eduoffer_read_permission')
@register.assignment_tag
def check_eduoffer_read_permission(user, eduoffer):
    return has_eduoffer_read_permission(user, eduoffer)


@register.filter(name='check_book_write_permission')
@register.assignment_tag
def check_book_write_permission(user, book):
    return has_book_write_permission(user, book)

@register.filter(name='check_book_read_permission')
@register.assignment_tag
def check_book_read_permission(user, book):
    return has_book_read_permission(user, book)


@register.filter(name='check_article_write_permission')
@register.assignment_tag
def check_article_write_permission(user, article):
    return has_article_write_permission(user, article)

@register.filter(name='check_article_read_permission')
@register.assignment_tag
def check_article_read_permission(user, article):
    return has_article_read_permission(user, article)


@register.filter(name='check_journalissue_write_permission')
@register.assignment_tag
def check_journalissue_write_permission(user, issue):
    return has_journalissue_write_permission(user, issue)

@register.filter(name='check_journalissue_read_permission')
@register.assignment_tag
def check_journalissue_read_permission(user, issue):
    return has_journalissue_read_permission(user, issue)
