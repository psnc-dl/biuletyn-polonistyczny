import os

from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import logout
from django.contrib.auth.views import password_reset, password_reset_confirm, password_reset_complete, password_reset_done
from django.contrib.flatpages import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views import static
from django.views.generic import TemplateView

from bportal.account.newsletter.views import newsletter, cancel_newsletter, generate_newsletter
from bportal.account.profile.views import user_profile
from bportal.auth.forms import PasswordResetForm, SetPasswordForm
from bportal.auth.views import register, activate
from bportal.main.views import home, contact, subscribe, base_url_json
from bportal.module.article.autocompletes import ArticleAutocomplete
from bportal.module.article.views import ArticleCreateView, ArticleDetailView, ArticleUpdateView, ArticleDeleteView
from bportal.module.article.views import article_list, article_list_pdf, article_pdf, article_csv
from bportal.module.book.autocompletes import BookAutocomplete
from bportal.module.book.views import BookCreateView, BookDetailView, BookUpdateView, BookDeleteView
from bportal.module.book.views import book_list, book_list_pdf, book_pdf, book_csv
from bportal.module.common.autocompletes import TargetGroupAutocomplete, ResearchDisciplineAutocomplete, PublicationCategoryAutocomplete, RegionAutocomplete, CityAutocomplete, TagAutocomplete, CountryAutocomplete
from bportal.module.common.view import DownloadView, TestView
from bportal.module.competition.autocompletes import CompetitionAutocomplete
from bportal.module.competition.views import CompetitionCreateView, CompetitionDetailView, CompetitionUpdateView, CompetitionDeleteView
from bportal.module.competition.views import competition_list, competition_list_pdf, competition_pdf, competition_csv
from bportal.module.dissertation.autocompletes import DissertationAutocomplete
from bportal.module.dissertation.views import DissertationCreateView, DissertationDetailView, DissertationUpdateView, DissertationDeleteView  
from bportal.module.dissertation.views import dissertation_list, dissertation_list_pdf, dissertation_pdf, dissertation_csv
from bportal.module.educationaloffer.autocompletes import EducationalOfferModeAutocomplete, EducationalOfferTypeAutocomplete, EducationalOfferAutocomplete
from bportal.module.educationaloffer.views import EducationalOfferCreateView, EducationalOfferDetailView, EducationalOfferUpdateView, EducationalOfferDeleteView
from bportal.module.educationaloffer.views import educationaloffer_list, educationaloffer_list_pdf, educationaloffer_pdf, educationaloffer_csv
from bportal.module.event.autocompletes import EventCategoryAutocomplete, EventAutocomplete
from bportal.module.event.views import EventCreateView, EventDetailView, EventDeleteView, EventUpdateView
from bportal.module.event.views import EventSummaryCreateView, EventSummaryDetailView, EventSummaryUpdateView, EventSummaryDeleteView
from bportal.module.event.views import event_list, event_list_by_day, event_list_pdf, event_pdf, event_csv
from bportal.module.institution.autocompletes import InstitutionTypeAutocomplete, InstitutionAutocomplete
from bportal.module.institution.views import InstitutionDetailView
from bportal.module.joboffer.autocompletes import JobOfferDisciplineAutocomplete, JobOfferTypeAutocomplete, JobOfferAutocomplete
from bportal.module.joboffer.views import JobOfferCreateView, JobOfferDetailView, JobOfferUpdateView, JobOfferDeleteView
from bportal.module.joboffer.views import joboffer_list, joboffer_list_pdf, joboffer_pdf, joboffer_csv
from bportal.module.journal.autocompletes import JournalAutocomplete, JournalIssueAutocomplete
from bportal.module.journal.views import JournalDetailView
from bportal.module.journal.views import JournalIssueCreateView, JournalIssueDetailView, JournalIssueUpdateView, JournalIssueDeleteView
from bportal.module.journal.views import journalissue_list, journalissue_list_pdf, journalissue_pdf, journalissue_csv
from bportal.module.new.autocompletes import NewCategoryAutocomplete
from bportal.module.new.views import NewCreateView, NewDetailView, NewUpdateView, NewDeleteView
from bportal.module.new.views import new_list, new_list_pdf, new_pdf, new_csv
from bportal.module.offers.views import offers_list
from bportal.module.person.autocompletes import ScientificTitleAutocomplete, PersonAutocomplete
from bportal.module.person.views import PersonCreateView, PersonDetailView
from bportal.module.project.autocompletes import ProjectAutocomplete
from bportal.module.project.views import ProjectCreateView, ProjectDetailView, ProjectUpdateView, ProjectDeleteView  
from bportal.module.project.views import project_list, project_list_pdf, project_pdf, project_csv
from bportal.module.publications.views import publications_list 
from bportal.module.research.views import research_list
from bportal.module.scholarship.autocompletes import ScholarshipTypeAutocomplete, ScholarshipAutocomplete
from bportal.module.scholarship.views import ScholarshipCreateView, ScholarshipDetailView, ScholarshipUpdateView, ScholarshipDeleteView
from bportal.module.scholarship.views import scholarship_list, scholarship_list_pdf, scholarship_pdf, scholarship_csv
from bportal.search.views import SearchView
from bportal.settings import BPORTAL_CONTACT_EMAIL_ADDRES_FROM


admin.autodiscover()


urlpatterns = [
               
    # MAIN PAGE
    url(r'^$', home, name='home'),
    url(r'^contact/$', contact, name='contact'),
    url(r'^subscribe/$', subscribe, name='subscribe'),
    
    # # BASE_URL
    url(r'base_url/$', base_url_json, name='base_url'),
    
    # # MEDIA & STATIC
    url(r'^media/(?P<path>.*)$', static.serve, {'document_root': os.path.join(os.path.dirname(__file__),
                                                'media/')}),
    url(r'^static/(?P<path>.*)$', static.serve, {'document_root': os.path.join(os.path.dirname(__file__),
                                                 'static/')}),
    # # LOGOUT
    url(r'^logout/$', logout, {'next_page': 'home'}, name='logout'),
    
    # # SOCIAL LOGIN
    url(r'^auth/', include('social_django.urls', namespace='social')),
 
    # # USERPROFILE
    url(r'^registration/register/$', register, name='registration'),
    url(r'^registration/activate/$', activate, name='activate'),
        
    url(r'^ilostmypassword/$', password_reset, {'template_name': 'bportal/auth/password_reset_form.html',
                                                'password_reset_form': PasswordResetForm, 
                                                'from_email': BPORTAL_CONTACT_EMAIL_ADDRES_FROM,
                                                'email_template_name': 'bportal/auth/password_reset_email.html' }, name='password_reset'),
    url(r'^ilostmypassword/sent/$', password_reset_done, {'template_name': 'bportal/auth/password_reset_done.html'}, name='password_reset_done'),
    url(r'^ilostmypassword/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
                            password_reset_confirm, {'template_name': 'bportal/auth/password_reset_confirm.html',
                                                     'set_password_form': SetPasswordForm}, name='password_reset_confirm'),
    url(r'^ilostmypassword/complete/$', password_reset_complete, {'template_name': 'bportal/auth//password_reset_complete.html'}, name='password_reset_complete'),
    url(r'^profile/$', user_profile, name='userprofile'),
    url(r'^admin/', include(admin.site.urls)),
    
    
    # # NEWSLETTER
    url(r'^newsletter/$', newsletter, name='newsletter'),
    url(r'^newsletter/cancel/$', cancel_newsletter, name='cancel_newsletter'),
    url(r'^newsletter/generate/$', generate_newsletter, name='generate_newsletter'),
    
    
    # # PROJECTS URLS
    url(r'^projects/$', project_list, name='project_list'),
    url(r'^projects/create$', ProjectCreateView.as_view(), name='project_create'),
    url(r'^projects/(?P<slug>[-\w\d]+),(?P<id>\d+)/details$', ProjectDetailView.as_view(), name='project_detail'),
    url(r'^projects/(?P<id>\d+)/edit$', ProjectUpdateView.as_view(), name='project_edit'),
    url(r'^projects/(?P<id>\d+)/delete$', ProjectDeleteView.as_view(), name='project_delete'),
    url(r'^projects/pdf$', project_pdf, name='project_pdf'),
    url(r'^projects/csv$', project_csv, name="project_csv"),
    url(r'^projects/list_pdf$', project_list_pdf, name='project_list_pdf'),


    # # DISSERTATION URLS
    url(r'^dissertations/$', dissertation_list, name='dissertation_list'),
    url(r'^dissertations/create$', DissertationCreateView.as_view(), name='dissertation_create'),
    url(r'^dissertations/(?P<slug>[-\w\d]+),(?P<id>\d+)/details$', DissertationDetailView.as_view(), name='dissertation_detail'),
    url(r'^dissertations/(?P<id>\d+)/edit$', DissertationUpdateView.as_view(), name='dissertation_edit'),
    url(r'^dissertations/(?P<id>\d+)/delete$', DissertationDeleteView.as_view(), name='dissertation_delete'),
    url(r'^dissertation/pdf$', dissertation_pdf, name='dissertation_pdf'),
    url(r'^dissertation/csv$', dissertation_csv, name='dissertation_csv'),
    url(r'^dissertation/list_pdf$', dissertation_list_pdf, name='dissertation_list_pdf'),
  
                                            
    # # COMPETITIONS
    url(r'^competitions/$', competition_list, name='competition_list'),
    url(r'^competitions/create$', CompetitionCreateView.as_view(), name='competition_create'),
    url(r'^competitions/(?P<slug>[-\w\d]+),(?P<id>\d+)/details$', CompetitionDetailView.as_view(), name='competition_detail'),
    url(r'^competitions/(?P<id>\d+)/edit$', CompetitionUpdateView.as_view(), name='competition_edit'),
    url(r'^competitions/(?P<id>\d+)/delete$', CompetitionDeleteView.as_view(), name='competition_delete'),
    url(r'^competitions/pdf$', competition_pdf, name='competition_pdf'),
    url(r'^competitions/csv$', competition_csv, name='competition_csv'),
    url(r'^competitions/list_pdf$', competition_list_pdf, name='competition_list_pdf'),
     

    # # JOBOFFERS URLS
    url(r'^joboffers/$', joboffer_list, name='joboffer_list'),
    url(r'^joboffers/create$', JobOfferCreateView.as_view(), name='joboffer_create'),
    url(r'^joboffers/(?P<slug>[-\w\d]+),(?P<id>\d+)/details$', JobOfferDetailView.as_view(), name='joboffer_detail'),
    url(r'^joboffers/(?P<id>\d+)/edit$', JobOfferUpdateView.as_view(), name='joboffer_edit'),
    url(r'^joboffers/(?P<id>\d+)/delete$', JobOfferDeleteView.as_view(), name='joboffer_delete'),
    url(r'^joboffers/pdf$', joboffer_pdf, name='joboffer_pdf'),
    url(r'^joboffers/csv$', joboffer_csv, name='joboffer_csv'),
    url(r'^joboffers/list_pdf$', joboffer_list_pdf, name='joboffer_list_pdf'),

    
    # # SCHOLARSHIPS URLS
    url(r'^scholarships/$', scholarship_list, name='scholarship_list'),
    url(r'^scholarships/create$', ScholarshipCreateView.as_view(), name='scholarship_create'),
    url(r'^scholarships/(?P<slug>[-\w\d]+),(?P<id>\d+)/details$', ScholarshipDetailView.as_view(), name='scholarship_detail'),
    url(r'^scholarships/(?P<id>\d+)/edit$', ScholarshipUpdateView.as_view(), name='scholarship_edit'),
    url(r'^scholarships/(?P<id>\d+)/delete$', ScholarshipDeleteView.as_view(), name='scholarship_delete'),
    url(r'^scholarships/pdf$', scholarship_pdf, name='scholarship_pdf'),
    url(r'^scholarships/csv$', scholarship_csv, name='scholarship_csv'),
    url(r'^scholarships/list_pdf$', scholarship_list_pdf, name='scholarship_list_pdf'),


    # # EDUOFFERS URLS
    url(r'^eduoffers/$', educationaloffer_list, name='eduoffer_list'),
    url(r'^eduoffers/create$', EducationalOfferCreateView.as_view(), name='eduoffer_create'),
    url(r'^eduoffers/(?P<slug>[-\w\d]+),(?P<id>\d+)/details$', EducationalOfferDetailView.as_view(), name='eduoffer_detail'),
    url(r'^eduoffers/(?P<id>\d+)/edit$', EducationalOfferUpdateView.as_view(), name='eduoffer_edit'),
    url(r'^eduoffers/(?P<id>\d+)/delete$', EducationalOfferDeleteView.as_view(), name='eduoffer_delete'),
    url(r'^eduoffers/pdf$', educationaloffer_pdf, name='eduoffer_pdf'),
    url(r'^eduoffers/csv$', educationaloffer_csv, name='eduoffers_csv'),
    url(r'^eduoffers/list_pdf$', educationaloffer_list_pdf, name='eduoffer_list_pdf'), 


    # # EVENTS URLS
    url(r'^events/$', event_list, name='event_list'),
    url(r'^events/(?P<day>\d{4}-\d{2}-\d{2})/$', event_list_by_day, name='event_list_by_day'),
    url(r'^events/create$', EventCreateView.as_view(), name='event_create'),
    url(r'^events/(?P<slug>[-\w\d]+),(?P<id>\d+)/details$', EventDetailView.as_view(), name='event_detail'),
    url(r'^events/(?P<id>\d+)/edit$', EventUpdateView.as_view(), name='event_edit'),
    url(r'^events/(?P<id>\d+)/delete$', EventDeleteView.as_view(), name='event_delete'),
    url(r'^events/pdf$', event_pdf, name='event_pdf'),
    url(r'^events/csv$', event_csv, name='event_csv'),
    url(r'^events/list_pdf$', event_list_pdf, name='event_list_pdf'),
    url(r'^events/summary/create$', EventSummaryCreateView.as_view(), name='event_summary_create'),
    url(r'^events/summary/(?P<slug>[-\w\d]+),(?P<id>\d+)/details$', EventSummaryDetailView.as_view(), name='event_summary_detail'),
    url(r'^events/summary/(?P<id>\d+)/edit$', EventSummaryUpdateView.as_view(), name='event_summary_edit'),
    url(r'^events/summary/(?P<id>\d+)/delete$', EventSummaryDeleteView.as_view(), name='event_summary_delete'),

    
    # # NEWS URLS
    url(r'^news/$', new_list, name='new_list'),
    url(r'^news/create$', NewCreateView.as_view(), name='new_create'),
    url(r'^news/(?P<slug>[-\w\d]+),(?P<id>\d+)/details$', NewDetailView.as_view(), name='new_detail'),
    url(r'^news/(?P<id>\d+)/edit$', NewUpdateView.as_view(), name='new_edit'),
    url(r'^news/(?P<id>\d+)/delete$', NewDeleteView.as_view(), name='new_delete'),    
    url(r'^news/pdf$', new_pdf, name='new_pdf'),
    url(r'^news/csv$', new_csv, name='new_csv'),
    url(r'^news/list_pdf$', new_list_pdf, name='new_list_pdf'),
    
    # # ARTICLES URLS
    url(r'^articles/$', article_list, name='article_list'),
    url(r'^articles/create$', ArticleCreateView.as_view(), name='article_create'),
    url(r'^articles/(?P<slug>[-\w\d]+),(?P<id>\d+)/details$', ArticleDetailView.as_view(), name='article_detail'),
    url(r'^articles/(?P<id>\d+)/edit$', ArticleUpdateView.as_view(), name='article_edit'),
    url(r'^articles/(?P<id>\d+)/delete$', ArticleDeleteView.as_view(), name='article_delete'),    
    url(r'^articles/pdf$', article_pdf, name='article_pdf'),
    url(r'^articles/csv$', article_csv, name='article_csv'),
    url(r'^articles/list_pdf$', article_list_pdf, name='article_list_pdf'),

    # # BOOKS URLS
    url(r'^books/$', book_list, name='book_list'),
    url(r'^books/create$', BookCreateView.as_view(), name='book_create'),
    url(r'^books/(?P<slug>[-\w\d]+),(?P<id>\d+)/details$', BookDetailView.as_view(), name='book_detail'),
    url(r'^books/(?P<id>\d+)/edit$', BookUpdateView.as_view(), name='book_edit'),
    url(r'^books/(?P<id>\d+)/delete$', BookDeleteView.as_view(), name='book_delete'),
    url(r'^books/pdf$', book_pdf, name='book_pdf'),
    url(r'^book/csv$', book_csv, name='book_csv'),
    url(r'^book/list_pdf$', book_list_pdf, name='book_list_pdf'),
    
    # # JOURNALS URLS
    url(r'^journals/(?P<slug>[-\w\d]+),(?P<id>\d+)/details$', JournalDetailView.as_view(), name='journal_detail'),
    url(r'^journals/issues/$', journalissue_list, name='journalissue_list'),
    url(r'^journals/issues/create$', JournalIssueCreateView.as_view(), name='journalissue_create'),
    url(r'^journals/issues/(?P<slug>[-\w\d]+),(?P<id>\d+)/details$', JournalIssueDetailView.as_view(), name='journalissue_detail'),
    url(r'^journals/issues/(?P<id>\d+)/edit$', JournalIssueUpdateView.as_view(), name='journalissue_edit'),
    url(r'^journals/issues/(?P<id>\d+)/delete$', JournalIssueDeleteView.as_view(), name='journalissue_delete'),
    url(r'^journals/issues/pdf$', journalissue_pdf, name='journalissue_pdf'),
    url(r'^journal/issue/csv$', journalissue_csv, name='journalissue_csv'),
    url(r'^journal/issue/list_pdf$', journalissue_list_pdf, name='journalissue_list_pdf'),


    # # INSTITUTIONS URLS
    url(r'^institutions/(?P<slug>[-\w\d]+),(?P<id>\d+)/details$', InstitutionDetailView.as_view(), name='institution_detail'),

    # # RESEARCH URLS
    url(r'^research/$', research_list, name='research_list'),
    
    # # OFFERS URLS
    url(r'^offers/$', offers_list, name='offers_list'),

    # # PUBLICATIONS URLS
    url(r'^publications/$', publications_list, name='publications_list'),


    # # PERSON URLS
    url(r'^people/create$', PersonCreateView.as_view(), name='person_create'),
    url(r'^people/(?P<slug>[-\w\d]+),(?P<id>\d+)/details$', PersonDetailView.as_view(), name='person_detail'),
       
       
    # autocomplete
    url(r'^targetgroup-autocomplete/$', TargetGroupAutocomplete.as_view(), name='targetgroup-autocomplete',),
    url(r'^researchdiscipline-autocomplete/$', ResearchDisciplineAutocomplete.as_view(), name='researchdiscipline-autocomplete',),
    url(r'^city-autocomplete/$', CityAutocomplete.as_view(), name='city-autocomplete',),
    url(r'^region-autocomplete/$', RegionAutocomplete.as_view(), name='region-autocomplete',),
    url(r'^country-autocomplete/$', CountryAutocomplete.as_view(), name='country-autocomplete',),
    url(r'^tag-autocomplete/$', TagAutocomplete.as_view(), name='tag-autocomplete',),
    
    url(r'^institutiontype-autocomplete/$', InstitutionTypeAutocomplete.as_view(), name='institutiontype-autocomplete',),
    url(r'^institution-autocomplete/$', InstitutionAutocomplete.as_view(), name='institution-autocomplete',),

    url(r'^scientifictitle-autocomplete/$', ScientificTitleAutocomplete.as_view(), name='scientifictitle-autocomplete',),
    url(r'^person-autocomplete/$', PersonAutocomplete.as_view(), name='person-autocomplete',),
    
    url(r'^project-autocomplete/$', ProjectAutocomplete.as_view(), name='project-autocomplete',),
    
    url(r'^dissertation-autocomplete/$', DissertationAutocomplete.as_view(), name='dissertation-autocomplete',),
    
    url(r'^competition-autocomplete/$', CompetitionAutocomplete.as_view(), name='competition-autocomplete',),
    
    url(r'^jobofferdiscipline-autocomplete/$', JobOfferDisciplineAutocomplete.as_view(), name='jobofferdiscipline-autocomplete',),
    url(r'^joboffertype-autocomplete/$', JobOfferTypeAutocomplete.as_view(), name='joboffertype-autocomplete',),
    url(r'^joboffer-autocomplete/$', JobOfferAutocomplete.as_view(), name='joboffer-autocomplete',),
    
    url(r'^scholarshiptype-autocomplete/$', ScholarshipTypeAutocomplete.as_view(), name='scholarshiptype-autocomplete',),
    url(r'^scholarship-autocomplete/$', ScholarshipAutocomplete.as_view(), name='scholarship-autocomplete',),    
    
    url(r'^educationaloffermode-autocomplete/$', EducationalOfferModeAutocomplete.as_view(), name='educationaloffermode-autocomplete',),
    url(r'^educationaloffertype-autocomplete/$', EducationalOfferTypeAutocomplete.as_view(), name='educationaloffertype-autocomplete',),
    url(r'^educationaloffer-autocomplete/$', EducationalOfferAutocomplete.as_view(), name='educationaloffer-autocomplete',),
    
    url(r'^eventcategory-autocomplete/$', EventCategoryAutocomplete.as_view(), name='eventcategory-autocomplete',),
    url(r'^event-autocomplete/$', EventAutocomplete.as_view(), name='event-autocomplete',),
    
    url(r'^book-autocomplete/$', BookAutocomplete.as_view(), name='book-autocomplete',),
    
    url(r'^article-autocomplete/$', ArticleAutocomplete.as_view(), name='article-autocomplete',),
    
    url(r'^journal-autocomplete/$', JournalAutocomplete.as_view(), name='journal-autocomplete',),
    url(r'^journalissue-autocomplete/$', JournalIssueAutocomplete.as_view(), name='journalissue-autocomplete',),    
        
    url(r'^newcategory-autocomplete/$', NewCategoryAutocomplete.as_view(), name='newcategory-autocomplete',),

    url(r'^publicationcategory-autocomplete/$', PublicationCategoryAutocomplete.as_view(), name='publicationcategory-autocomplete',),

    
    # # FLAT PAGES
    url(r'^pages/', include('django.contrib.flatpages.urls')),
    url(r'^about/$', views.flatpage, {'url': '/about/'}, name='about'),
    url(r'^partners/$', views.flatpage, {'url': '/partners/'}, name='partners'),
    url(r'^editors/$', views.flatpage, {'url': '/editors/'}, name='editors'),
    url(r'^faq/$', views.flatpage, {'url': '/faq/'}, name='faq'),
    url(r'^cookie/$', views.flatpage, {'url': '/cookie/'}, name='cookie_policy'),


    # # downloads
    url(r'^download/$', DownloadView.as_view(), name='download'),
    

    # # SEARCH URL (HAYSTACK)
    url(r'^search/$', SearchView.as_view(), name='search_view'),
                       
                       
    # # CKEDITOR URLS
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),                       
                           
    # # CAPTCHA URLS
    url(r'^captcha/', include('captcha.urls')),
    
    # # robots.txt
    url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    
    # # test headers
    url(r'^test/headers/$', TestView.as_view(), name='test_headers'),
    
] + staticfiles_urlpatterns()
 
