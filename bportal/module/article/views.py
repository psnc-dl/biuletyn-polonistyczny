# -*- coding: utf-8 -*-
import csv

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.html import strip_tags
from django.views import generic
from django.views.generic import DetailView
from extra_views import UpdateWithInlinesView, CreateWithInlinesView
import reversion

from bportal.account.profile.models import UserProfile
from bportal.account.profile.utils import UserConfig
from bportal.module.article.forms import ArticleConfirmAdminForm
from bportal.module.common import pdf
from bportal.module.common.permissions import has_create_permission
from bportal.module.common.utils import ExtendedPaginator
from bportal.module.common.utils import remove_unnecessary_tags_from_title, slugify_text_title
from bportal.module.common.view import ChangeMessageView

from .filters import ArticleFilter
from .forms import ArticleForm, ArticleFileInline, ArticleLinkInline, ArticleContentContributionInline
from .messages import MessageArticle
from .models import Article, ArticleAuthorized, ArticleModification
from .permissions import check_article_write_permission, check_article_read_permission


def article_query(request):
    GET = request.GET.copy()

    article_only_my = GET.get('article_only_my')

    user = request.user
    filter_args = [];
    published = Q(article_is_accepted=True)
    owner = Q(article_added_by=user)
    modif = Q(article_modified_by=user)
    if user.is_authenticated():
        if not user.is_superuser:
            profile = UserProfile.objects.get(user=user)
            inst = Q(article_authorizations__in=profile.user_institution.all())
            filter_args.append(published | owner | modif | inst)
    else:
        filter_args.append(published)

    if article_only_my:
        only_my = Q(article_added_by=user)
        filter_args.append(only_my)
        
    # distinct because of many article_authorizations that give duplicates in joins 
    qset = Article.objects.filter(*filter_args).distinct()
    return [qset, filter_args, GET]        


def article_filtering(request):
    query_result = article_query(request)
    qset = query_result[0]
    GET = query_result[2]
    
    o = GET.get('o', None)
    if not o:
        GET['o'] = '-article_is_promoted,-article_date_add'
        o = GET.get('o')
        
    f = ArticleFilter(GET, queryset=qset)
    per_page = UserConfig.getPerPage(request, GET)
    paginator = Paginator(f.qs, per_page)
    
    page = GET.get('page', None)
    if page is not None:
        page = int(page)
    else:
        page = 1
    try:
        p = paginator.page(page)
    except PageNotAnInteger:
        p = paginator.page(1)
    except EmptyPage:
        p = paginator.page(paginator.num_pages)
         
    response_dict = dict()
    response_dict['filter'] = f
    response_dict['curr_page'] = p
    response_dict['per_page'] = per_page
    response_dict['o'] = o
    response_dict['per_page_choices'] = UserConfig.perPageChoices()
    response_dict['pagination_prefix'] = ExtendedPaginator.construct_filter_string(f.data)
    
    return response_dict, page

    
def article_list(request):
    response_dict, _ = article_filtering(request)
    return render_to_response('bportal_modules/details/articles/list.html', response_dict, RequestContext(request))


def article_pdf(request):
    article_id = request.GET['article_id']
    template_name = "bportal_modules/details/articles/details_pdf.html"
    article = Article.objects.get(article_id=article_id)
    context = {"article": article, }
    return pdf.generateHttpResponse(request, context, template_name)


def article_list_pdf(request):
    template_name = "bportal_modules/details/articles/list_pdf.html"
    query_result, _ = article_filtering(request)           
    context = {"articles": query_result['filter'].qs, }
    return pdf.generateHttpResponse(request, context, template_name)


def article_csv(request):
    query_result, _ = article_filtering(request)     
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="articles.csv"'
    writer = csv.writer(response, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for q in query_result['filter'].qs:
        writer.writerow([q.article_title_text, q.article_lead])
    return response


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'bportal_modules/details/articles/details.html'
    pk_url_kwarg = 'id'        
    slug_field = 'article_title_slug'
    query_pk_and_slug = True
    
    def get_object(self, *args, **kwargs):     
        article = super(ArticleDetailView, self).get_object(*args, **kwargs)
            
        response_dict, article.curr_page = article_filtering(self.request)
        article.filter = response_dict['filter'] if 'filter' in response_dict else None
        article.per_page = response_dict['per_page'] if 'per_page' in response_dict else None
                
        return check_article_read_permission(self.request.user, article)
    
    def get_context_data(self, **kwargs):
        context = super(ArticleDetailView, self).get_context_data(**kwargs)
        context['meta'] = self.get_object().as_meta(self.request)
        return context


class ArticleCreateView(CreateWithInlinesView, ChangeMessageView):
    model = Article
    form_class = ArticleForm
    inlines = [ArticleFileInline, ArticleLinkInline, ArticleContentContributionInline]
    template_name = 'bportal_modules/details/articles/create.html'
    duplicate = False
    
    @method_decorator(login_required)
    @method_decorator(user_passes_test(test_func=has_create_permission))
    def dispatch(self, request, *args, **kwargs):
        force = ('force' in request.POST)
        try: 
            title = request.POST['article_title']
            title = remove_unnecessary_tags_from_title(title)
            title = strip_tags(title)
            dup_list = Article.objects.filter(article_title_text=title)  
            if dup_list:         
                if (self.form_class is not ArticleConfirmAdminForm) and (not force):
                    self.duplicate = True
                    messages.add_message(request, messages.ERROR, MessageArticle.DUPLICATE)
                else:
                    self.form_class = ArticleForm
                    self.duplicate = False
            else:
                self.duplicate = False
        except KeyError:
            self.duplicate = False
        return super(ArticleCreateView, self).dispatch(request, *args, **kwargs)
        
    def get_form_class(self):
        return ArticleConfirmAdminForm if self.duplicate else self.form_class

    def forms_valid(self, form, inlines):
        if self.duplicate:
            return self.forms_invalid(form, inlines)
        user = self.request.user
        form.instance.article_added_by = user
        form.instance.article_modified_by = user
        form.instance.article_title = remove_unnecessary_tags_from_title(form.instance.article_title)
        form.instance.article_title_text = strip_tags(form.instance.article_title)        
        form.instance.article_title_slug = slugify_text_title(form.instance.article_title_text)

        response = super(ArticleCreateView, self).forms_valid(form, inlines)
        
        modification = ArticleModification.objects.create(article=self.object, user=user, date_time=timezone.now())
        profile = UserProfile.objects.get(user=user) 
        for institution in profile.user_institution.all():
            ArticleAuthorized.objects.create(article=self.object, authorized=institution)
        profile.user_last_edit_date_time = modification.date_time
        profile.save()
        
        change_message = self.construct_change_message(form, inlines, True)
        reversion.set_comment(change_message)        
        
        return response


class ArticleUpdateView(UpdateWithInlinesView, ChangeMessageView):
    model = Article
    form_class = ArticleForm
    inlines = [ArticleFileInline, ArticleLinkInline, ArticleContentContributionInline]
    template_name = 'bportal_modules/details/articles/edit.html'
    pk_url_kwarg = 'id'    
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ArticleUpdateView, self).dispatch(*args, **kwargs)
    
    def get_object(self, *args, **kwargs):
        article = super(ArticleUpdateView, self).get_object(*args, **kwargs)
        return check_article_write_permission(self.request.user, article)
    
    def forms_valid(self, form, inlines):
        user = self.request.user
        form.instance.article_modified_by = user
        form.instance.article_date_edit = timezone.now()
        form.instance.article_title = remove_unnecessary_tags_from_title(form.instance.article_title)
        form.instance.article_title_text = strip_tags(form.instance.article_title)       
        form.instance.article_title_slug = slugify_text_title(form.instance.article_title_text)        

        response = super(ArticleUpdateView, self).forms_valid(form, inlines)

        modification = ArticleModification.objects.create(article=self.object, user=user, date_time=timezone.now())
        profile = UserProfile.objects.get(user=user)
        profile.user_last_edit_date_time = modification.date_time
        profile.save()
        
        change_message = self.construct_change_message(form, inlines, False)
        reversion.set_comment(change_message)
                
        return response


class ArticleDeleteView(generic.DeleteView):
    model = Article
    template_name = 'bportal_modules/details/articles/delete.html'
    pk_url_kwarg = 'id'
    success_url = reverse_lazy('article_list')
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ArticleDeleteView, self).dispatch(*args, **kwargs)
    
    def get_object(self, *args, **kwargs):
        article = super(ArticleDeleteView, self).get_object(*args, **kwargs)
        return check_article_write_permission(self.request.user, article)
