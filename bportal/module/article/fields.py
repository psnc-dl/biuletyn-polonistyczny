# -*- coding: utf-8 -*-
class FieldArticle():
    VERBOSE_NAME = 'Artykuł / wywiad'
    VERBOSE_NAME_PLURAL = 'Artykuły i wywiady'
    TITLE = 'Tytuł'
    LEAD = 'Akapit wprowadzający'    
    DESCRIPTION = 'Opis artykułu/wywiadu'    
    IMAGE = 'Zdjęcie'
    IMAGE_COPYRIGHT = 'Prawa autorskie do zdjęcia'
    IMAGE_CAPTION = 'Informacje o zdjęciu'
    DATE_ADD = 'Data dodania'
    DATE_EDIT = 'Data edycji'
    KEYWORDS = 'Słowa kluczowe'
    ADDED_BY = 'Dodany przez'
    AUTHORIZED = 'Uprawnieni'
    MODIFIED_BY = 'Zmodyfikowany przez'  
    IS_ACCEPTED = 'Opublikuj'
    IS_PROMOTED = 'Artykuł/wywiad promowany'

class FieldArticleFile():
    VERBOSE_NAME = 'plik dołączony do artykułu/wywiadu'
    VERBOSE_NAME_PLURAL = 'pliki dołączone do artykułów/wywiadów'
    METADATA = 'Metadane pliku'
    ARTICLE = 'Artykuł / wywiad'
    FILE = 'Plik'
    COPYRIGHT = 'Prawa autorskie/licencja'

class FieldArticleLink():
    VERBOSE_NAME = 'link powiązany z artykułem/wywiadem'
    VERBOSE_NAME_PLURAL = 'linki powiązane z artykułami/wywiadami'
    ARTICLE = 'Artykuł'
    LINK = 'Link' 
    
class FieldArticleContentContribution():
    VERBOSE_NAME = 'rola osoby we wkład treści'
    VERBOSE_NAME_PLURAL = 'role osoby we wkład treści'
    ARTICLE= 'Artykuł'
    PERSON = 'Osoba'
    ROLE = 'Rola'
   
class FieldArticleAuthorized():    
    VERBOSE_NAME = 'uprawnienia instytucji do artykułu/wywiadu'
    VERBOSE_NAME_PLURAL = 'uprawnienia instytucji do artykułów i wywiadów'
    AUTHORIZED = 'Uprawnienie'
    ARTICLE = 'Artykuł' 
        
class FieldArticleModification():
    VERBOSE_NAME = 'modyfikacja artykułu / wywiadu'
    VERBOSE_NAME_PLURAL = 'modyfikacje artykułów i wywiadów'
    ARTICLE = 'Artykuł'
    USER = 'Użytkownik'
    DATE_TIME = 'Data i czas'

class FieldArticleFilter():
    STATUS = 'Status'
    ONLY_MY = 'Tylko moje artykuły i wywiady'
