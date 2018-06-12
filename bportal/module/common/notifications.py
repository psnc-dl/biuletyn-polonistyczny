# -*- coding: utf-8 -*-
import logging
import threading

from django.contrib.auth.models import User
from django.core.mail.message import EmailMessage
from django.dispatch.dispatcher import receiver
import reversion

from bportal.module import joboffer
from bportal.module.article.fields import FieldArticle
from bportal.module.article.models import Article, ArticleAuthorized
from bportal.module.book.fields import FieldBook
from bportal.module.book.models import Book, BookAuthorized
from bportal.module.competition.fields import FieldCompetition
from bportal.module.competition.models import Competition, CompetitionAuthorized
from bportal.module.dissertation.fields import FieldDissertation
from bportal.module.dissertation.models import Dissertation, DissertationAuthorized
from bportal.module.educationaloffer.fields import FieldEducationalOffer
from bportal.module.educationaloffer.models import EducationalOffer, EducationalOfferAuthorized
from bportal.module.event.fields import FieldEvent, FieldEventSummary
from bportal.module.event.models import Event, EventAuthorized, EventSummary
from bportal.module.joboffer.fields import FieldJobOffer
from bportal.module.joboffer.models import JobOffer, JobOfferAuthorized
from bportal.module.journal.fields import FieldJournalIssue
from bportal.module.journal.models import JournalIssue, JournalIssueAuthorized
from bportal.module.new.fields import FieldNew
from bportal.module.new.models import New, NewAuthorized
from bportal.module.project.fields import FieldProject
from bportal.module.project.models import Project, ProjectAuthorized
from bportal.module.scholarship.fields import FieldScholarship
from bportal.module.scholarship.models import Scholarship, ScholarshipAuthorized
from bportal.settings import BPORTAL_HOST, BPORTAL_PORT, BPORTAL_CONTACT_EMAIL_ADDRES_FROM


logger = logging.getLogger(__name__)


@receiver(reversion.signals.post_revision_commit)
def on_revision_commit(sender, revision, versions, **kwargs):
    # 'Initial version.' comes from the python3 manage.py createinitialrevisions commands
    # None or empty string come from import
    # In such cases do not notify anybody  
    if revision.comment is not None and revision.comment != '' and revision.comment != 'Initial version.':
        logger.debug('revision to notify: ' + revision.comment)
        NotificationThread(revision, versions).start()


class NotificationThread(threading.Thread):

    ENTITY_TYPE_MASCULINE = 'MASCULINE'
    ENTITY_TYPE_FEMININE = 'FEMININE'
    ENTITY_TYPE_NEUTER = 'NEUTER'

    def __init__(self, revision, versions):
        self.revision = revision
        self.versions = versions
        threading.Thread.__init__(self)

    def run(self):
        user = self.revision.user
        add = self.revision.comment.startswith('Dodany.')
        if add:
            subject = 'Nowa treść w Biuletynie Polonistycznym'
        else:
            subject = 'Modyfikacja treści w Biuletynie Polonistycznym'
        sender = 'Biuletyn Polonistyczny ' + '<' + BPORTAL_CONTACT_EMAIL_ADDRES_FROM + '>'
        
        object_id, title, absolute_url, content_type, entity_type = self.find_main_version_with_type()
        logger.debug('parsed revision: ' + object_id + '; ' + title + '; ' + absolute_url + '; ' + content_type)
        
        html_content, change_message = self.construct_notification_message(user, object_id, title, absolute_url, content_type, entity_type, add)
        logger.debug('notification message: ' + html_content)
        
        if change_message == 'Żadne pole nie zmienione.' or change_message == 'Zmieniono':
            logger.debug('email will not be sent since there was no change actually')
        else:
                                
            authorized_institutions = self.find_authorized_institutions(object_id, content_type)
            logger.debug('authorized institutions: ' + ', '.join(ai.institution_shortname for ai in authorized_institutions))

            editors = User.objects.filter(userprofile__user_institution__in=authorized_institutions, userprofile__user_is_editor=True).all()
            logger.debug('editors: ' + ', '.join(e.username for e in editors))
        
            admins = User.objects.filter(is_superuser=True)
            logger.debug('admins: ' + ', '.join(a.username for a in admins))
        
            recipients = set()
            recipients.update(editors)
            recipients.update(admins)
            recipients.remove(user)
            logger.debug('recipients: ' + ', '.join(r.username for r in recipients))
        
            recipient_emails = []
            for recipient in recipients:
                if recipient.email:
                    recipient_emails.append(recipient.first_name + ' ' + recipient.last_name + ' <' + recipient.email + '>')
            logger.debug('recipient emails: ' + ', '.join(recipient_emails))        

            if recipient_emails:        
                logger.debug('sending email: ' + subject)
                msg = EmailMessage(subject, html_content, sender, recipient_emails)
                msg.send()
                logger.info('email sent: ' + html_content)
            else:
                logger.debug('email will not be sent since anybody, except the user, is watching the institutions')

    def find_main_version_with_type(self):
        for version in self.versions:
            if version.content_type.model == 'project':
                project = Project.objects.get(project_id=version.object_id)
                return [version.object_id, project.project_title_text, project.get_absolute_url(), 'project', self.ENTITY_TYPE_MASCULINE]
            elif version.content_type.model == 'dissertation':
                dissertation = Dissertation.objects.get(dissertation_id=version.object_id)
                return [version.object_id, dissertation.dissertation_title_text, dissertation.get_absolute_url(), 'dissertation', self.ENTITY_TYPE_FEMININE]
            elif version.content_type.model == 'competition':
                competition = Competition.objects.get(competition_id=version.object_id)
                return [version.object_id, competition.competition_title_text, competition.get_absolute_url(), 'competition', self.ENTITY_TYPE_MASCULINE]
            elif version.content_type.model == 'joboffer':
                joboffer = JobOffer.objects.get(joboffer_id=version.object_id)
                return [version.object_id, joboffer.joboffer_position_text, joboffer.get_absolute_url(), 'joboffer', self.ENTITY_TYPE_FEMININE]
            elif version.content_type.model == 'scholarship':
                scholarship = Scholarship.objects.get(scholarship_id=version.object_id)
                return [version.object_id, scholarship.scholarship_name_text, scholarship.get_absolute_url(), 'scholarship', self.ENTITY_TYPE_NEUTER]
            elif version.content_type.model == 'educationaloffer':
                eduoffer = EducationalOffer.objects.get(eduoffer_id=version.object_id)
                return [version.object_id, eduoffer.eduoffer_position_text, eduoffer.get_absolute_url(), 'eduoffer', self.ENTITY_TYPE_FEMININE]
            elif version.content_type.model == 'eventsummary':
                event_summary = EventSummary.objects.get(event_summary_id=version.object_id)
                return [version.object_id, event_summary.event_summary_event.event_name_text, event_summary.get_absolute_url(), 'event_summary', self.ENTITY_TYPE_NEUTER]
            elif version.content_type.model == 'event':
                for other_version in self.versions:   # check whether event summary occurs
                    if other_version.content_type.model == 'eventsummary':
                        event_summary = EventSummary.objects.get(event_summary_id=other_version.object_id)
                        return [other_version.object_id, event_summary.event_summary_event.event_name_text, event_summary.get_absolute_url(), 'event_summary', self.ENTITY_TYPE_NEUTER]
                event = Event.objects.get(event_id=version.object_id)
                return [version.object_id, event.event_name_text, event.get_absolute_url(), 'event', self.ENTITY_TYPE_NEUTER]
            elif version.content_type.model == 'new':
                new = New.objects.get(new_id=version.object_id)
                return [version.object_id, new.new_title_text, new.get_absolute_url(), 'new', self.ENTITY_TYPE_FEMININE]                                    
            elif version.content_type.model == 'article':
                article = Article.objects.get(article_id=version.object_id)
                return [version.object_id, article.article_title_text, article.get_absolute_url(), 'article', self.ENTITY_TYPE_MASCULINE]                                    
            elif version.content_type.model == 'book':
                book = Book.objects.get(book_id=version.object_id)
                return [version.object_id, book.book_title_text, book.get_absolute_url(), 'book', self.ENTITY_TYPE_FEMININE]                                    
            elif version.content_type.model == 'journalissue':
                journalissue = JournalIssue.objects.get(journalissue_id=version.object_id)
                return [version.object_id, journalissue.journalissue_title_text, journalissue.get_absolute_url(), 'journalissue', self.ENTITY_TYPE_MASCULINE]
        return [None, None, None, None, None]
         
    def get_entity_name(self, content_type):
        if content_type == 'project':
            return 'Projekt'
        elif content_type == 'dissertation':
            return 'Rozprawa'
        elif content_type == 'competition':
            return 'Konkurs'
        elif content_type == 'joboffer':
            return 'Oferta pracy'
        elif content_type == 'scholarship':
            return 'Stypendium'
        elif content_type == 'eduoffer':
            return 'Oferta edukacyjna'
        elif content_type == 'event_summary':
            return 'Sprawozdanie z wydarzenia'
        elif content_type == 'event':
            return 'Wydarzenie'
        elif content_type == 'new':
            return 'Aktualność'        
        elif content_type == 'article':
            return 'Artykuł/wywiad'
        elif content_type == 'book':
            return 'Nowość wydawnicza'        
        elif content_type == 'journalissue':
            return 'Numer czasopisma'
        else:
            return None
        
    def construct_notification_message(self, user, object_id, title, absolute_url, content_type, entity_type, add):
        notification_message = 'Szanowni Państwo,\n\n'
        notification_message = notification_message + self.get_entity_name(content_type)
        if add:
            if entity_type == self.ENTITY_TYPE_MASCULINE:
                notification_message = notification_message + ' został dodany: '
            elif entity_type == self.ENTITY_TYPE_FEMININE:
                notification_message = notification_message + ' została dodana: '
            elif entity_type == self.ENTITY_TYPE_NEUTER:
                notification_message = notification_message + ' zostało dodane: '
        else:
            if entity_type == self.ENTITY_TYPE_MASCULINE:
                notification_message = notification_message + ' został zmodyfikowny: '
            elif entity_type == self.ENTITY_TYPE_FEMININE:
                notification_message = notification_message + ' została zmodyfikowana: '
            elif entity_type == self.ENTITY_TYPE_NEUTER:
                notification_message = notification_message + ' zostało zmodyfikowane: '
        notification_message = notification_message + title
        notification_message = notification_message + ' ('
        notification_message = notification_message + self.construct_host()
        notification_message = notification_message + absolute_url
        notification_message = notification_message + ')\n\n'                  
                  
        notification_message = notification_message + 'Użytkownik: '
        notification_message = notification_message + user.first_name
        notification_message = notification_message + ' '
        notification_message = notification_message + user.last_name
        notification_message = notification_message + ' ('
        notification_message = notification_message + user.username
        notification_message = notification_message + ')'
        notification_message = notification_message + '\n\n'
                
        change_message = self.internationalize_fields_of_revision_comment(content_type)       
        
        notification_message = notification_message + change_message
        notification_message = notification_message + '\n\n'
                
        notification_message = notification_message + 'BiuletynPolonistyczny.pl\n'
        return [notification_message, change_message] 

    def internationalize_fields_of_revision_comment(self, content_type):
        comment = self.revision.comment
        # special case - event_summary points that event was changed. It's not true
        comment = comment.replace(' i event_summary_event', '')
        comment = comment.replace(' event_summary_event', '')
        labels = self.get_labels_of_entity(content_type)
        for key in labels:
            field = content_type + '_' + key.lower()
            if isinstance(labels[key], str):
                comment = comment.replace(field, labels[key])
        # insert a dot where it is missing
        comment = self.insert_missing_into_comment(comment, ' Dodano')
        comment = self.insert_missing_into_comment(comment, ' Usunięto')
        comment = self.insert_missing_into_comment(comment, ' Zmieniono') 
        return comment     
            
    def insert_missing_into_comment(self, comment, phrase):
        idx = comment.find(phrase)
        if idx != -1 and comment.find('.', idx - 1, idx) == -1:
            comment = comment.replace(phrase, '.' + phrase, 1)
        return comment        
            
    def get_labels_of_entity(self, content_type):
        if content_type == 'project':
            return vars(FieldProject)
        elif content_type == 'dissertation':
            return vars(FieldDissertation)
        elif content_type == 'competition':
            return vars(FieldCompetition)
        elif content_type == 'joboffer':
            return vars(FieldJobOffer)
        elif content_type == 'scholarship':
            return vars(FieldScholarship)
        elif content_type == 'eduoffer':
            return vars(FieldEducationalOffer)
        elif content_type == 'event_summary':
            return vars(FieldEventSummary)        
        elif content_type == 'event':
            return vars(FieldEvent)
        elif content_type == 'new':
            return vars(FieldNew)     
        elif content_type == 'article':
            return vars(FieldArticle)
        elif content_type == 'book':
            return vars(FieldBook)
        elif content_type == 'journalissue':
            return vars(FieldJournalIssue)
        else:
            return None

    def construct_host(self):
        host = ''
        if BPORTAL_PORT:
            host = host + BPORTAL_HOST[:-1]
            host = host + ':'
            host = host + BPORTAL_PORT
        else:
            host = host + BPORTAL_HOST[:-1]
        return host

    def find_authorized_institutions(self, object_id, content_type):
        institutions = []
        if content_type == 'project':
            project_authorizeds = ProjectAuthorized.objects.filter(project__project_id=object_id)
            for project_authorized in project_authorizeds:
                institutions.append(project_authorized.authorized)
        elif content_type == 'dissertation':
            dissertation_authorizeds = DissertationAuthorized.objects.filter(dissertation__dissertation_id=object_id)
            for dissertation_authorized in dissertation_authorizeds:
                institutions.append(dissertation_authorized.authorized)       
        elif content_type == 'competition':
            competition_authorizeds = CompetitionAuthorized.objects.filter(competition__competition_id=object_id)
            for competition_authorized in competition_authorizeds:
                institutions.append(competition_authorized.authorized) 
        elif content_type == 'joboffer':
            joboffer_authorizeds = JobOfferAuthorized.objects.filter(joboffer__joboffer_id=object_id)
            for joboffer_authorized in joboffer_authorizeds:
                institutions.append(joboffer_authorized.authorized) 
        elif content_type == 'scholarship':
            scholarship_authorizeds = ScholarshipAuthorized.objects.filter(scholarship__scholarship_id=object_id)
            for scholarship_authorized in scholarship_authorizeds:
                institutions.append(scholarship_authorized.authorized) 
        elif content_type == 'eduoffer':
            eduoffer_authorizeds = EducationalOfferAuthorized.objects.filter(eduoffer__eduoffer_id=object_id)
            for eduoffer_authorized in eduoffer_authorizeds:
                institutions.append(eduoffer_authorized.authorized)
        elif content_type == 'event_summary':
            event_authorizeds = EventAuthorized.objects.filter(event__event_summary__event_summary_id=object_id)
            for event_authorized in event_authorizeds:
                institutions.append(event_authorized.authorized)
        elif content_type == 'event':
            event_authorizeds = EventAuthorized.objects.filter(event__event_id=object_id)
            for event_authorized in event_authorizeds:
                institutions.append(event_authorized.authorized)
        elif content_type == 'new':
            new_authorizeds = NewAuthorized.objects.filter(new__new_id=object_id)
            for new_authorized in new_authorizeds:
                institutions.append(new_authorized.authorized)
        elif content_type == 'article':
            article_authorizeds = ArticleAuthorized.objects.filter(article__article_id=object_id)
            for article_authorized in article_authorizeds:
                institutions.append(article_authorized.authorized)
        elif content_type == 'book':
            book_authorizeds = BookAuthorized.objects.filter(book__book_id=object_id)
            for book_authorized in book_authorizeds:
                institutions.append(book_authorized.authorized)
        elif content_type == 'journalissue':
            journalissue_authorizeds = JournalIssueAuthorized.objects.filter(journalissue__journalissue_id=object_id)
            for journalissue_authorized in journalissue_authorizeds:
                institutions.append(journalissue_authorized.authorized)
        return institutions         
