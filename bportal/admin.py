# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.flatpages.models import FlatPage

from bportal.account.newsletter.admins import NewsletterConfigAdmin, ManagementEmailAdmin,\
    NewsletterCustomContentAdmin
from bportal.account.newsletter.models import NewsletterConfig, ManagementEmail,\
    NewsletterCustomContent
from bportal.account.profile.admins import UserAdmin
from bportal.flatpage.admins import FlatPageAdmin   
from bportal.module.article.admins import ArticleAdmin
from bportal.module.article.models import Article
from bportal.module.book.admins import BookAdmin
from bportal.module.book.models import Book
from bportal.module.common.admins import TargetGroupAdmin, ResearchDisciplineAdmin, PublicationCategoryAdmin
from bportal.module.common.models import TargetGroup, ResearchDiscipline, PublicationCategory
from bportal.module.competition.admins import CompetitionAdmin
from bportal.module.competition.models import Competition
from bportal.module.dissertation.admins import DissertationAdmin
from bportal.module.dissertation.models import Dissertation
from bportal.module.educationaloffer.admins import EducationalOfferAdmin, EducationalOfferModeAdmin, EducationalOfferTypeAdmin
from bportal.module.educationaloffer.models import EducationalOffer, EducationalOfferMode, EducationalOfferType
from bportal.module.event.admins import EventAdmin, EventSummaryAdmin, EventCategoryAdmin
from bportal.module.event.models import Event, EventSummary, EventCategory
from bportal.module.institution.admins import InstitutionTypeAdmin, InstitutionAdmin, InstitutionRoleAdmin
from bportal.module.institution.models import InstitutionType, Institution, InstitutionRole
from bportal.module.joboffer.admins import JobOfferAdmin, JobOfferDisciplineAdmin, JobOfferTypeAdmin
from bportal.module.joboffer.models import JobOffer, JobOfferDiscipline, JobOfferType
from bportal.module.journal.admins import JournalAdmin, JournalIssueAdmin
from bportal.module.journal.models import Journal, JournalIssue
from bportal.module.new.admins import NewAdmin, NewCategoryAdmin
from bportal.module.new.models import New, NewCategory
from bportal.module.person.admins import PersonAdmin, PersonContributionRoleAdmin
from bportal.module.person.models import Person, PersonContributionRole
from bportal.module.project.admins import ProjectAdmin
from bportal.module.project.models import Project
from bportal.module.scholarship.admins import ScholarshipAdmin, ScholarshipTypeAdmin
from bportal.module.scholarship.models import Scholarship, ScholarshipType


admin.autodiscover()

admin.site.register(TargetGroup, TargetGroupAdmin)
admin.site.register(ResearchDiscipline, ResearchDisciplineAdmin)
admin.site.register(PersonContributionRole, PersonContributionRoleAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(InstitutionType, InstitutionTypeAdmin)
admin.site.register(Institution, InstitutionAdmin)
admin.site.register(InstitutionRole, InstitutionRoleAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Dissertation, DissertationAdmin)
admin.site.register(Competition, CompetitionAdmin)
admin.site.register(JobOfferDiscipline, JobOfferDisciplineAdmin)
admin.site.register(JobOfferType, JobOfferTypeAdmin)
admin.site.register(JobOffer, JobOfferAdmin)
admin.site.register(ScholarshipType, ScholarshipTypeAdmin)
admin.site.register(Scholarship, ScholarshipAdmin)
admin.site.register(EducationalOfferMode, EducationalOfferModeAdmin)
admin.site.register(EducationalOfferType, EducationalOfferTypeAdmin)
admin.site.register(EducationalOffer, EducationalOfferAdmin)
admin.site.register(EventCategory, EventCategoryAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(EventSummary, EventSummaryAdmin)
admin.site.register(PublicationCategory, PublicationCategoryAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(NewCategory, NewCategoryAdmin)
admin.site.register(New, NewAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Journal, JournalAdmin)
admin.site.register(JournalIssue, JournalIssueAdmin)
admin.site.register(NewsletterConfig, NewsletterConfigAdmin)
admin.site.register(ManagementEmail, ManagementEmailAdmin)
admin.site.register(NewsletterCustomContent, NewsletterCustomContentAdmin)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Unregister Group
admin.site.unregister(Group)

# Re-register FlatPage
admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)
