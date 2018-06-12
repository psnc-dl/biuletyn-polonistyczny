# -*- coding: utf-8 -*-
class FieldNew():
    VERBOSE_NAME = 'Aktualność'
    VERBOSE_NAME_PLURAL = 'Aktualności'
    TITLE = 'Tytuł'
    LEAD = 'Akapit wprowadzający'
    DESCRIPTION = 'Opis'
    CATEGORY = 'Kategoria'  
    CATEGORIES = 'Kategorie'
    IMAGE = 'Obraz'
    IMAGE_COPYRIGHT = 'Prawa/licencja do obrazu'
    IMAGE_CAPTION = 'Informacje o zdjęciu'
    DATE_ADD = 'Data dodania'
    DATE_EDIT = 'Data edycji'
    RELATED_EVENT = 'Dotyczy wydarzenia'
    RELATED_PROJECT = 'Dotyczy projektu'
    RELATED_DISSERTATION = 'Dotyczy rozprawy'
    RELATED_COMPETITION = 'Dotyczy konkursy'
    RELATED_JOBOFFER = 'Dotyczy oferty pracy'
    RELATED_EDUOFFER = 'Dotyczy oferty edukacyjnej'
    RELATED_SCHOLARSHIP  = 'Dotyczy stypendium'
    RELATED_BOOK  = 'Dotyczy nowości wydawniczej'
    RELATED_ARTICLE  = 'Dotyczy artykułu/wywiadu'
    RELATED_JOURNALISSUE  = 'Dotyczy numeru czasopisma'         
    KEYWORDS = 'Słowa kluczowe'
    CONTRIBUTORS = 'Autorzy/Rozmówcy/Opublikowali'
    ADDED_BY = 'Dodany przez'    
    MODIFIED_BY = 'Zmodyfikowany przez'
    IS_ACCEPTED = 'Opublikuj'    
    IS_PROMOTED = 'Aktualność promowana'
    
    DATE_CONVERSION = 'Data'
    LINK = 'Link'
    IS_INTERNAL = 'Link wewnętrzny'
    FILE = 'Plik'
    
class FieldNewCategory():
    VERBOSE_NAME = 'kategoria aktualności'
    VERBOSE_NAME_PLURAL = 'kategorie aktualności'
    NAME = 'Kategoria'
    ITEM_NAME = 'Element Kategorii'
    
class FieldNewFile():
    VERBOSE_NAME = 'plik dołączony do aktualności'
    VERBOSE_NAME_PLURAL = 'pliki dołączone do aktualności'
    METADATA = 'Metadane pliku'
    NEW = 'Aktualność'
    FILE = 'Plik'
    COPYRIGHT = 'Prawa autorskie/licencja'

class FieldNewLink():
    VERBOSE_NAME = 'link powiązany z aktualnością'
    VERBOSE_NAME_PLURAL = 'linki powiązane z aktualnościami'
    NEW = 'Aktualność'
    LINK = 'Link' 
    
class FieldNewContentContribution():
    VERBOSE_NAME = 'rola osoby we wkład treści'
    VERBOSE_NAME_PLURAL = 'role osoby we wkład treści'
    NEW = 'Aktualność'
    PERSON = 'Osoba'
    ROLE = 'Rola'

class FieldNewAuthorized():    
    VERBOSE_NAME = 'uprawnienia instytucji do aktualności'
    VERBOSE_NAME_PLURAL = 'uprawnienia instytucji do aktualności'
    AUTHORIZED = 'Uprawnienie'
    NEW = 'Aktualność' 
        
class FieldNewModification():
    VERBOSE_NAME = 'modyfikacja aktualności'
    VERBOSE_NAME_PLURAL = 'modyfikacje aktualności'
    NEW = 'Aktualność'
    USER = 'Użytkownik'
    DATE_TIME = 'Data i czas'

class FieldNewFilter():
    ONLY_MY = 'Tylko moje wydarzenia'

