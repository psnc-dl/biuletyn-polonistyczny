# -*- coding: utf-8 -*-
from haystack import indexes

from bportal.module.book.models import Book
from bportal.module.competition.models import Competition
from bportal.module.dissertation.models import Dissertation
from bportal.module.educationaloffer.models import EducationalOffer
from bportal.module.event.models import Event
from bportal.module.institution.models import Institution
from bportal.module.joboffer.models import JobOffer
from bportal.module.person.models import Person
from bportal.module.project.models import Project
from bportal.module.scholarship.models import Scholarship
from bportal.module.article.models import Article
from bportal.module.journal.models import JournalIssue, Journal


class ProjectIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    
    def get_model(self):
        return Project

    
class DissertationIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    
    def get_model(self):
        return Dissertation    

    
class CompetitionIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    
    def get_model(self):
        return Competition    
       
    
class EducationalOfferIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    
    def get_model(self):
        return EducationalOffer
    

class ScholarshipIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
     
    def get_model(self):
        return Scholarship


class JobOfferIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
     
    def get_model(self):
        return JobOffer
    
    
class EventIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    
    def get_model(self):
        return Event


class BookIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
     
    def get_model(self):
        return Book

class ArticleIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
     
    def get_model(self):
        return Article

class JournalIssueIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
     
    def get_model(self):
        return JournalIssue
    
class JournalIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
     
    def get_model(self):
        return Journal
    
class PersonIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
        
    def get_model(self):
        return Person 
    

class InstitutionIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    
    def get_model(self):
        return Institution
