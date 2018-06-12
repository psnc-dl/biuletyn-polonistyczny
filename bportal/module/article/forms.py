# -*- coding: utf-8 -*-
from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from dal import autocomplete
from django import forms
from django.core.urlresolvers import reverse_lazy
from django.forms.widgets import Textarea
from django.utils.html import strip_tags
from django_addanother.widgets import AddAnotherWidgetWrapper
from extra_views.advanced import InlineFormSet

from bportal.module.common.fields import FieldBaseConfirm
from bportal.module.common.forms import NoHistoryBooleanField, BaseConfirmModelForm, HistoryTagField
from bportal.module.common.utils import remove_unnecessary_tags_from_title
from bportal.module.common.widgets import FileWidget

from .fields import FieldArticle, FieldArticleLink, FieldArticleFile
from .messages import MessageArticle
from .models import Article, ArticleFile, ArticleLink, ArticleContentContribution


class AbstractArticleForm(forms.ModelForm):
    article_title = forms.CharField(label=FieldArticle.TITLE, widget=CKEditorWidget(config_name='titles'))
    article_lead = forms.CharField(label=FieldArticle.LEAD, widget=CKEditorWidget(config_name='leads'))        
    article_image_copyright = forms.CharField(label=FieldArticle.IMAGE_COPYRIGHT, widget=Textarea(attrs={'style' : 'height : auto', 'rows': 2}), required=False)
    article_description = forms.CharField(label=FieldArticle.DESCRIPTION, widget=CKEditorUploadingWidget())                     
    article_keywords = HistoryTagField(label=FieldArticle.KEYWORDS)
                       
    class Meta:
        abstract = True
        model = Article
        fields = ('__all__')
        exclude = ('article_title_text', 'article_title_slug', 'article_date_add', 'article_date_edit', 'article_added_by', 'article_modified_by', 'article_authorizations',
                   'article_contributors')


class ArticleAdminForm(AbstractArticleForm):
    force = NoHistoryBooleanField(label=FieldBaseConfirm.FORCE, required=False, initial=False, widget=forms.widgets.HiddenInput())

    class Meta(AbstractArticleForm.Meta):
        pass
    

class ArticleConfirmAdminForm(ArticleAdminForm):
        
    def clean(self):
        cleaned_data = super(ArticleConfirmAdminForm, self).clean()
        force = cleaned_data['force']
        if force:
            return cleaned_data
        if 'article_title' in cleaned_data:
            name = cleaned_data['article_title']
            name = remove_unnecessary_tags_from_title(name)
            name = strip_tags(name)   
            dup_list = Article.objects.filter(article_title_text=name)
            if dup_list:
                self.fields['force'].widget = forms.widgets.CheckboxInput()
                self.fields['force'].required = True
                self.fields['force'].initial = False
                raise forms.ValidationError(MessageArticle.DUPLICATE)
        return cleaned_data  
    
    class Meta(ArticleAdminForm.Meta):
        pass


class ArticleForm(AbstractArticleForm):
    article_image = forms.ImageField(label=FieldArticle.IMAGE, widget=FileWidget(), required=False)
    
    class Meta(AbstractArticleForm.Meta):
        exclude = ('article_title_text', 'article_title_slug', 'article_date_add', 'article_date_edit', 'article_added_by', 'article_modified_by', 'article_authorizations', 'article_is_promoted',
                   'article_contributors')        
        
    class Media:
        # # they are not loaded by AddAnotherWidgetWrapper widget
        # # probably widget media do not work in inlines 
        # # force these media in the form        
        css = {
            'all': (
                'autocomplete_light/vendor/select2/dist/css/select2.css',
                'autocomplete_light/select2.css',
                'django_addanother/addanother.css',
            )            
        }
        js = (
            'autocomplete_light/jquery.init.js',
            'autocomplete_light/autocomplete.init.js',
            'autocomplete_light/vendor/select2/dist/js/select2.full.js',
            'autocomplete_light/select2.js',            
            'django_addanother/django_jquery.js',
            'admin/js/admin/RelatedObjectLookups.js',
        )
        
        
class ConfirmArticleModelForm(ArticleForm, BaseConfirmModelForm):
    pass


class ArticleFileForm(forms.ModelForm):
    file = forms.FileField(label=FieldArticleFile.FILE, widget=FileWidget())
    copyright = forms.CharField(label=FieldArticleFile.COPYRIGHT, widget=Textarea(attrs={'style' : 'height : auto', 'rows': 2}), required=False)
    
    class Meta:
        model = ArticleFile
        exclude = ('article',)
        
        
class ArticleFileInline(InlineFormSet):
    model = ArticleFile
    form_class = ArticleFileForm
    extra = 1
    

class ArticleLinkForm(forms.ModelForm):
    link = forms.URLField(label=FieldArticleLink.LINK)
    
    class Meta:
        model = ArticleLink
        exclude = ('article',)
        
        
class ArticleLinkInline(InlineFormSet):
    model = ArticleLink
    form_class = ArticleLinkForm
    extra = 1


class ArticleContentContributionAdminForm(forms.ModelForm):
    
    class Meta:
        model = ArticleContentContribution
        widgets = {
            'person': autocomplete.ModelSelect2(url='person-autocomplete'),
            'role': autocomplete.Select2(attrs={'class': 'select2'}),
            }
        exclude = ('article',)


class ArticleContentContributionForm(forms.ModelForm):
    
    class Meta:
        model = ArticleContentContribution
        widgets = {
            'person': AddAnotherWidgetWrapper(autocomplete.ModelSelect2(url='person-autocomplete'), reverse_lazy('person_create'),),
            'role': autocomplete.Select2(attrs={'class': 'select2'}),
            }
        exclude = ('article',)


class ArticleContentContributionInline(InlineFormSet):
    model = ArticleContentContribution
    form_class = ArticleContentContributionForm
    extra = 1
