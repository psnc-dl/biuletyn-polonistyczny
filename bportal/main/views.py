# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core.mail.message import EmailMessage
from django.db.models import Q
from django.http.response import JsonResponse, HttpResponse
from django.shortcuts import render_to_response 
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

from bportal.account.newsletter.models import NEWSPERIOD_MONTH, NewsletterConfig
from bportal.account.profile.models import UserProfile
from bportal.module.book.models import Book
from bportal.module.competition.models import Competition
from bportal.module.dissertation.models import Dissertation
from bportal.module.educationaloffer.models import EducationalOffer
from bportal.module.event.models import Event, EventCategory
from bportal.module.event.utils import get_events_calendar_list, get_events_calendar_before_first_day, get_events_calendar_after_last_day
from bportal.module.joboffer.models import JobOffer
from bportal.module.new.models import New
from bportal.module.project.models import Project
from bportal.module.scholarship.models import Scholarship
from bportal.settings import BPORTAL_CONTACT_EMAIL_ADDRES_FROM, BPORTAL_CONTACT_EMAIL_ADDRES_TO, BPORTAL_BASE_URL

from .forms import ContactMessageForm, NewsletterSubscriptionForm
from bportal.module.article.models import Article
from bportal.module.journal.models import JournalIssue


def home(request):
    user = request.user
    if user.is_authenticated(): 
        promoted_projects = Project.objects.all().filter(Q(project_is_promoted = True) & (Q(project_is_accepted = True) | Q(project_added_by = user) | Q(project_modified_by = user)))
        promoted_job_offers = JobOffer.objects.all().filter(Q(joboffer_is_promoted = True) & (Q(joboffer_is_accepted = True) | Q(joboffer_added_by = user) | Q(joboffer_modified_by = user)))
        promoted_edu_offers = EducationalOffer.objects.all().filter(Q(eduoffer_is_promoted = True) & (Q(eduoffer_is_accepted = True) | Q(eduoffer_added_by = user) | Q(eduoffer_modified_by = user)))
        promoted_scholarships = Scholarship.objects.all().filter(Q(scholarship_is_promoted = True) & (Q(scholarship_is_accepted = True) | Q(scholarship_added_by = user) | Q(scholarship_modified_by = user)))
        promoted_dissertations = Dissertation.objects.all().filter(Q(dissertation_is_promoted = True) & (Q(dissertation_is_accepted = True) | Q(dissertation_added_by = user) | Q(dissertation_modified_by = user)))
        promoted_competitions = Competition.objects.all().filter(Q(competition_is_promoted = True) & (Q(competition_is_accepted = True) | Q(competition_added_by = user) | Q(competition_modified_by = user)))                
        promoted_events = Event.objects.all().filter(Q(event_is_promoted = True) & (Q(event_is_accepted = True) | Q(event_added_by = user) | Q(event_modified_by = user)))
        promoted_articles = Article.objects.all().filter(Q(article_is_promoted = True) & (Q(article_is_accepted = True) | Q(article_added_by = user) | Q(article_modified_by = user)))
        promoted_books = Book.objects.all().filter(Q(book_is_promoted=True) & (Q(book_is_accepted=True) | Q(book_added_by=user) | Q(book_modified_by=user)))
        promoted_journals = JournalIssue.objects.all().filter(Q(journalissue_is_promoted=True) & (Q(journalissue_is_accepted=True) | Q(journalissue_added_by=user) | Q(journalissue_modified_by=user)))
    else:
        promoted_projects = Project.objects.all().filter(project_is_promoted = True, project_is_accepted = True)
        promoted_job_offers = JobOffer.objects.all().filter(joboffer_is_promoted = True, joboffer_is_accepted = True)
        promoted_edu_offers = EducationalOffer.objects.all().filter(eduoffer_is_promoted = True, eduoffer_is_accepted = True)
        promoted_scholarships = Scholarship.objects.all().filter(scholarship_is_promoted = True, scholarship_is_accepted = True)
        promoted_dissertations = Dissertation.objects.all().filter(dissertation_is_promoted = True, dissertation_is_accepted = True)
        promoted_competitions = Competition.objects.all().filter(competition_is_promoted = True, competition_is_accepted = True)
        promoted_events = Event.objects.all().filter(event_is_promoted = True, event_is_accepted = True)
        promoted_articles = Article.objects.all().filter(article_is_promoted = True, article_is_accepted = True)
        promoted_books = Book.objects.all().filter(book_is_promoted=True, book_is_accepted=True)
        promoted_journals = JournalIssue.objects.all().filter(journalissue_is_promoted = True, journalissue_is_accepted = True)
        
    promoted_news = New.objects.all().filter(new_is_promoted=True).order_by('-new_date_add')
    
    events_calendar_list = get_events_calendar_list()
    events_calendar_before_first_day = get_events_calendar_before_first_day()
    events_calendar_after_last_day = get_events_calendar_after_last_day()
    
    message_form = ContactMessageForm()
    newsletter_form = NewsletterSubscriptionForm()
      
    return render_to_response('bportal/main/index.html', {
                                            'message_form' : message_form,
                                            'newsletter_form' : newsletter_form,
                                            'promoted_projects' : promoted_projects,
                                            'promoted_dissertations' : promoted_dissertations,
                                            'promoted_job_offers' : promoted_job_offers,
                                            'promoted_edu_offers' : promoted_edu_offers,
                                            'promoted_scholarships' : promoted_scholarships,
                                            'promoted_events' : promoted_events,
                                            'promoted_articles' : promoted_articles,
                                            'promoted_competitions' : promoted_competitions,
                                            'promoted_books' : promoted_books,
                                            'promoted_journals' : promoted_journals,
                                            'promoted_news' : promoted_news,
                                            'events_calendar_list' : events_calendar_list,
                                            'events_calendar_before_first_day' : events_calendar_before_first_day,
                                            'events_calendar_after_last_day' : events_calendar_after_last_day,
                                            },
                              RequestContext(request))


def contact(request):
    if request.method == 'GET':
        message_form = ContactMessageForm(request.GET)
        if not message_form.errors and message_form.is_valid :
            firstname = message_form.cleaned_data['firstname']
            email = message_form.cleaned_data['email']
            phone = message_form.cleaned_data['phone']
            title = message_form.cleaned_data['title']
            message = message_form.cleaned_data['message']
            message += ('\n\n' + '===')
            message += ('\n' + firstname)
            message += ('\n' + email)
            if phone is not None:
                message += ('\n' + str(phone))
            emailMessage = EmailMessage(title, message, firstname + '<' + BPORTAL_CONTACT_EMAIL_ADDRES_FROM + '>',
                                        [BPORTAL_CONTACT_EMAIL_ADDRES_TO], reply_to=[firstname + '<' + email + '>'])
            emailMessage.send(False)
        else:
            json = "{\"errors\": {"
            size = len(message_form.errors)
            i = 0
            for key, value in message_form.errors.items():
                json += ("\"" + key + "\"") 
                json += ":"
                error = str(value).replace("\"", "\\\"")
                json += ("\"" + error + "\"")
                i += 1
                if i < size:
                    json += (", ")
            json += "}}"
            return JsonResponse(json, safe=False, content_type='charset=UTF-8')
    data = '{\"ok\":\"Wiadomość została wysłana.\"}'
    return JsonResponse(data, safe=False, content_type='charset=UTF-8')     


def subscribe(request):
    if request.method == 'GET':
        newsletter_form = NewsletterSubscriptionForm(request.GET)
        if not newsletter_form.errors and newsletter_form.is_valid :
            email = str(newsletter_form.cleaned_data['news_email'])
            email_list = str(User.objects.all().values_list('email'))
            if email not in email_list:
                user_password = str(User.objects.make_random_password())
                user = User.objects.create_user(email, email, password=user_password)      
                user.save()
                profile = UserProfile.objects.create(user=user)
                profile.user_newsletter_flag = True
                profile.save()
                userNewsConfig = NewsletterConfig.objects.create(user=profile)
                userNewsConfig.period = NEWSPERIOD_MONTH
                userNewsConfig.dissertation = True
                userNewsConfig.competition = True
                userNewsConfig.joboffer = True
                userNewsConfig.eduoffer = True
                userNewsConfig.project = True
                userNewsConfig.scholarship = True
                userNewsConfig.event_categories = EventCategory.objects.all()
                userNewsConfig.save()
                data = '{\"ok\":\"Zapisałeś się na newsletter.\"}'
            else:
                data = '{\"ok\":\"Jesteś już zapisany na newsletter.\"}'
        else:
            json = "{\"errors\": {"
            size = len(newsletter_form.errors)
            i = 0
            for key, value in newsletter_form.errors.items():
                json += ("\"" + key + "\"") 
                json += ":"
                error = str(value).replace("\"", "\\\"")
                json += ("\"" + error + "\"")
                i += 1
                if i < size:
                    json += (", ")
            json += "}}"
            return JsonResponse(json, safe=False, content_type='charset=UTF-8')

    return JsonResponse(data, safe=False, content_type='charset=UTF-8')   

    
@csrf_exempt
def base_url_json(request):
    data = '{"base_url":"' + BPORTAL_BASE_URL + '"}'
    return HttpResponse(data, content_type='application/json; charset=UTF-8')
