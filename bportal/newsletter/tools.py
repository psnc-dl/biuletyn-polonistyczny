# -*- coding: utf-8 -*-
from datetime import date, timedelta
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core import mail
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.core.mail.message import EmailMessage
from django.db.models import Q
from django.http.response import HttpResponse
from django.template.context import Context
from django.template.loader import get_template
from django.utils import translation, timezone
import locale
import logging
import os
import uuid
import weasyprint

from bportal.account.newsletter.messages import MessageNewsletter
from bportal.account.newsletter.models import NEWSPERIOD_WEEK, NEWSPERIOD_TWO_WEEKS, NEWSPERIOD_MONTH, NewsletterConfig, NewsletterCustomContent
from bportal.module.competition.models import Competition
from bportal.module.dissertation.models import Dissertation
from bportal.module.educationaloffer.models import EducationalOffer
from bportal.module.event.models import Event, EventCategory
from bportal.module.joboffer.models import JobOffer
from bportal.module.project.models import Project
from bportal.module.scholarship.models import Scholarship
from bportal.settings import BPORTAL_CONTACT_EMAIL_ADDRES_FROM, MEDIA_ROOT, MEDIA_URL, BPORTAL_HOST
from openpyxl.chartsheet import custom
from builtins import Exception
from bportal.module.article.models import Article
from bportal.module.book.models import Book
from bportal.module.journal.models import JournalIssue
from bportal.module.new.models import New, NewCategory


logger = logging.getLogger(__name__)

class EmptyNewsletterException(Exception):
    pass

class NewsletterGenerator():
    fs = FileSystemStorage(location=MEDIA_ROOT + '/newsletters')
    
    def __init__(self):
        pass
    
    def __generateNewsHtmlContent(self, currUser=None):
        
        userNewsConfig = None
         
        if currUser is not None:
            userNewsConfig  = NewsletterConfig.objects.get(user=currUser.userprofile)
        
        #exception - newsletter not configured
        if userNewsConfig is None:
            raise Exception(MessageNewsletter.ERROR_NOT_CONFIGURED)
        
        option = userNewsConfig.period
        
        locale.setlocale(locale.LC_TIME, "pl_PL.utf8") 
        days_to_subtract = 0
        if option == NEWSPERIOD_WEEK:
            days_to_subtract = 7
        elif option == NEWSPERIOD_TWO_WEEKS:
            days_to_subtract = 14
        elif option == NEWSPERIOD_MONTH:
            days_to_subtract = 30
         
        d = date.today() - timedelta(days=days_to_subtract)   
        e = date.today() - timedelta(days=1)      
        
        #custom content
        custom_contents = NewsletterCustomContent.objects.filter(valid_until__gte=date.today()).filter(Q(valid_since__lte=date.today())|Q(valid_since=None))
        
        news = []
        projects = []
        dissertations = []
        competitions = []
        scholarships = []
        eduoffers = []
        joboffers = []
        events = []
        articles = []
        books = []
        journals_issues = []
        
        modules_list = [custom_contents, news, projects, dissertations, competitions, scholarships, eduoffers, joboffers, events, articles, books, journals_issues]
         
        if userNewsConfig.project:
            projects = Project.objects.filter(project_date_add__gte=d, project_is_accepted = True)
        if userNewsConfig.dissertation:
            dissertations = Dissertation.objects.filter(dissertation_date_add__gte=d, dissertation_is_accepted = True)
        if userNewsConfig.competition:
            competitions = Competition.objects.filter(competition_date_add__gte=d, competition_is_accepted = True)
        if userNewsConfig.scholarship:
            scholarships = Scholarship.objects.filter(scholarship_date_add__gte=d, scholarship_is_accepted = True)
        if userNewsConfig.eduoffer:
            eduoffers = EducationalOffer.objects.filter(eduoffer_date_add__gte=d, eduoffer_is_accepted = True)
        if userNewsConfig.joboffer:
            joboffers = JobOffer.objects.filter(joboffer_date_add__gte=d, joboffer_is_accepted = True)
        if userNewsConfig.article:
            articles = Article.objects.filter(article_date_add__gte=d, article_is_accepted = True)
        if userNewsConfig.book:
            books = Book.objects.filter(book_date_add__gte=d, book_is_accepted = True)
        if userNewsConfig.journal:
            journals_issues = JournalIssue.objects.filter(journalissue_date_add__gte=d, journalissue_is_accepted = True)
            
        user_UUID = str(uuid.uuid4())
        userNewsConfig.UUID = user_UUID  
        userNewsConfig.save()
         
        events = Event.objects.filter(event_date_add__gte=d, event_is_accepted = True)
        event_dict = {}
        event_cats_names={}
        event_categories = EventCategory.objects.values_list('event_category_id', 'event_category_name')  

        user_event_categories = userNewsConfig.event_categories.all().values_list('event_category_id', 'event_category_name')
        for ec in event_categories:
            if ec not in user_event_categories:
                continue
            event_cats_names[ec[0]] = ec[1]
            events_ids = [x.event_id for x in events if x.event_category.event_category_id == ec[0]]
            events_list = Event.objects.filter(event_id__in = events_ids)
            if (len(events_list) > 0):
                event_dict[ec[0]] = list()
                event_dict[ec[0]].append(events_list)
                
        
        news = New.objects.filter(new_date_add__gte=d, new_is_accepted = True)
        new_dict = {}
        new_cats_names={}
        new_categories = NewCategory.objects.values_list('new_category_id', 'new_category_name')  

        user_new_categories = userNewsConfig.new_categories.all().values_list('new_category_id', 'new_category_name')
        for nc in new_categories:
            if nc not in user_new_categories:
                continue
            new_cats_names[ec[0]] = ec[1]
            news_ids = [x.new_id for x in news if x.new_category.new_category_id == ec[0]]
            news_list = New.objects.filter(new_id__in = news_ids)
            if (len(news_list) > 0):
                new_dict[ec[0]] = list()
                new_dict[ec[0]].append(news_list)
        
        if all(len(m) == 0 for m in modules_list):
            userNewsConfig.last_sent = date.today()
            userNewsConfig.save()
            raise EmptyNewsletterException()
        
        context = {"projects": projects,
                   "dissertations": dissertations,
                   "competitions": competitions,
                   "scholarships": scholarships,
                   "eduoffers": eduoffers,
                   "joboffers": joboffers,
                   "events": event_dict,
                   "events_cats": event_cats_names,
                   "news": new_dict,
                   "news_cats": new_cats_names,
                   "articles": articles,
                   "books": books,
                   "journals_issues": journals_issues,
                   'host' : BPORTAL_HOST[:-1],  # assumed that / is the last char, it has to be
                   'media_prefix' : MEDIA_URL,
                   'today' : date.today(),
                   'datefrom' : d,
                   'dateto' :e,
                   'user_UUID':user_UUID,
                   "custom_contents": custom_contents,
                   }
        translation.activate('pl')
        template = get_template('bportal/newsletter/content.html')
        html = template.render(Context(context))
        return html
    
    def __checkLastSentDate(self, currUser):
        if currUser.userprofile is not None:
            userNewsConfig = None
            if currUser is not None:
                try:
                    userNewsConfig  = NewsletterConfig.objects.get(user=currUser.userprofile)
                except NewsletterConfig.DoesNotExist:
                    pass
            
            # newsletter is not configured
            if userNewsConfig is None:
                return False
            
            option = userNewsConfig.period
            
            days_to_subtract = 0
            if option == NEWSPERIOD_WEEK:
                days_to_subtract = 7
            elif option == NEWSPERIOD_TWO_WEEKS:
                days_to_subtract = 14
            elif option == NEWSPERIOD_MONTH:
                days_to_subtract = 30
            
            if userNewsConfig.last_sent is not None:
                d = date.today() - userNewsConfig.last_sent
                return d.days > days_to_subtract
            else: 
                return True
        else:
            return False
    
    def generateNewsHttpResponseForUser(self, user):
        response = HttpResponse(content_type="application/pdf")
        try:
            html = self.__generateNewsHtmlContent(user)
            weasyprint.HTML(string=html).write_pdf(response)
        except EmptyNewsletterException:
            pass
        except Exception as e:
            logger.error(e)
        
        return response
    
    def generateNewsPdfForUser(self, user):
        try:
            html = self.__generateNewsHtmlContent(user)    
            pdfFileContent = weasyprint.HTML(string=html).write_pdf()
            pdfFile = ContentFile(content=pdfFileContent)
            self.fs.save(str(user.id) + '.pdf', pdfFile)
        except Exception as e:
            pass
        
    def generateNewsPdfForAllUsers(self):
        try:
            for u in User.objects.all():
                #if self.__checkLastSentDate(u):
                self.generateNewsPdfForUser(u)
        except:
            pass
        
    def cleanAllNewsPdfs(self):
        try:
            path = MEDIA_ROOT + '/newsletters'
            [_, files] = self.fs.listdir(path)
            for fname in files:
                self.fs.delete(fname)
        except:
            pass
        



class NewsletterSender():
    
    def __init__(self):
        pass
    
    def __prepareMessagesQueue(self):
        manEmail = Site.objects.get_current().managementemail
        messagesList = []
        if manEmail is None:
            logger.debug('mail config does not exist')
            return messagesList
        
        for u in User.objects.all():
            userProfile = u.userprofile
            if (userProfile is not None) and (u.email is not None):
                #check if file to send exist
                path = MEDIA_ROOT + '/newsletters/' + str(u.id) + '.pdf'
                if not os.path.exists(path):
                    continue
                title = manEmail.title
                message = manEmail.message      
                emailMessage = EmailMessage(title, message, 'Redakcja Biuletynu Polonistycznego ' + '<' + BPORTAL_CONTACT_EMAIL_ADDRES_FROM + '>', 
                                        [u.email])
                filename = 'newsletter_biuletyn.pdf'
                with open(path, 'rb') as f:
                    content = f.read()
                emailMessage.attach(filename, content)
                messagesList.append(emailMessage)
                
                userNewsConfig = None
                userNewsConfig  = NewsletterConfig.objects.get(user=userProfile)
                
                # newsletter is not configured
                if userNewsConfig is None:
                    continue
                userNewsConfig.last_sent = date.today()
                userNewsConfig.save()
                
        return messagesList
    
    def sendNewsEmails(self):
        emailsList = self.__prepareMessagesQueue()
        
        with mail.get_connection(backend='django.core.mail.backends.smtp.EmailBackend') as connection:
            connection.open()
            connection.send_messages(emailsList)
            connection.close()
            