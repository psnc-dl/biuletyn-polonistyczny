# -*- coding: utf-8 -*-
class FieldEvent():
    VERBOSE_NAME = 'Wydarzenie'
    VERBOSE_NAME_PLURAL = 'Wydarzenia'
    NAME = 'Nazwa'
    LEAD = 'Akapit wprowadzający'    
    DESCRIPTION = 'Opis wydarzenia'    
    CATEGORY = 'Kategoria'
    CATEGORIES = 'Kategorie'
    TARGETS = 'Grupy docelowe'    
    DATE_FROM = 'Data rozpoczęcia wydarzenia'
    DATE_TO = 'Data zakończenia wydarzenia'
    TIME_FROM = 'Godzina rozpoczęcia wydarzenia'
    TIME_TO = 'Godzina zakończenia wydarzenia'
    CITY = 'Miasto'
    REGION = 'Województwo'
    COUNTRY = 'Kraj'
    INSTITUTIONS = 'Instytucje organizujące'
    ADDRESS = 'Adres'
    CONTRIBUTORS_DATE = 'Data zgłaszania prelegentów'
    CONTRIBUTORS_TIME = 'Godzina zgłaszania prelegentów'
    PARTICIPANTS_DATE = 'Data zgłaszania uczestników'
    PARTICIPANTS_TIME = 'Godzina zgłaszania uczestników'
    FEES = 'Opłata'
    POSTER = 'Plakat'
    POSTER_COPYRIGHT = 'Prawa autorskie do plakatu'
    POSTER_CAPTION = 'Informacje o plakacie'
    YOUTUBE_MOVIE = 'Link do filmu z YouTube'
    DATE_ADD = 'Data dodania'
    DATE_EDIT = 'Data edycji'
    KEYWORDS = 'Słowa kluczowe'
    CONNECTED_PROJECTS = 'Projekty powiązane z wydarzeniem'
    CONNECTED_DISSERTATIONS = 'Rozprawy powiązane z wydarzeniem'
    CONNECTED_COMPETITIONS = 'Konkursy powiązane z wydarzeniem'
    ADDED_BY = 'Dodany przez'
    AUTHORIZED = 'Uprawnieni'
    MODIFIED_BY = 'Zmodyfikowany przez'  
    IS_ACCEPTED = 'Opublikuj'
    IS_PROMOTED = 'Wydarzenie promowane'
        
class FieldEventCategory():
    VERBOSE_NAME = 'kategoria wydarzenia'
    VERBOSE_NAME_PLURAL = 'kategorie wydarzeń'
    NAME = 'Kategoria'

class FieldEventFile():
    VERBOSE_NAME = 'plik dołączony do wydarzenia'
    VERBOSE_NAME_PLURAL = 'pliki dołączone do wydarzeń'
    METADATA = 'Metadane pliku'
    EVENT = 'Wydarzenie'
    FILE = 'Plik'
    COPYRIGHT = 'Prawa autorskie/licencja'

class FieldEventLink():
    VERBOSE_NAME = 'link powiązany z wydarzeniem'
    VERBOSE_NAME_PLURAL = 'linki powiązane z wydarzeniem'
    EVENT = 'Wydarzenie'
    LINK = 'Link' 
    
class FieldEventContentContribution():
    VERBOSE_NAME = 'rola osoby we wkład treści'
    VERBOSE_NAME_PLURAL = 'role osoby we wkład treści'
    EVENT = 'Wydarzenie'
    PERSON = 'Osoba'
    ROLE = 'Rola'
   
class FieldEventSummary():
    VERBOSE_NAME = 'sprawozdanie z wydarzenia'
    VERBOSE_NAME_PLURAL = 'sprawozdania z wydarzeń'    
    LEAD = 'Akapit wprowadzający'
    DESCRIPTION = 'Sprawozdanie'
    DATE_ADD = 'Data dodania'
    ADDED_BY = 'Dodany przez'
    EVENT = 'Wydarzenie'
    
class FieldEventSummaryFile():
    VERBOSE_NAME = 'plik dołączony do sprawozdania'
    VERBOSE_NAME_PLURAL = 'pliki dołączone do sprawozdań'
    METADATA = 'Metadane pliku'
    EVENT_SUMMARY = 'Sprawozdanie z wydarzenia'
    FILE = 'Plik'
    COPYRIGHT = 'Prawa autorskie/licencja'

class FieldEventSummaryLink():
    VERBOSE_NAME = 'link powiązany ze sprawozdaniem z wydarzenia'
    VERBOSE_NAME_PLURAL = 'linki powiązane ze sprawozdaniami z wydarzeń'
    EVENT_SUMMARY = 'Sprawozdanie z wydarzenia'
    LINK = 'Link'
    
class FieldEventSummaryPicture():
    VERBOSE_NAME = 'zdjęcie dołączone do sprawozdania'
    VERBOSE_NAME_PLURAL = 'zdjęcia dołączone do sprawozdań'
    METADATA = 'Metadane pliku'
    EVENT_SUMMARY = 'Sprawozdanie z wydarzenia'
    FILE = 'Zdjęcie'
    COPYRIGHT = 'Prawa autorskie/licencja'
    DESCRIPTION = 'Opis'

class FieldEventSummaryPublication():
    VERBOSE_NAME = 'publikacja dołączona do sprawozdania z wydarzenia'
    VERBOSE_NAME_PLURAL = 'publikacje dołączone do sprawozdań z wydarzeń'
    EVENT_SUMMARY = 'Sprawozdanie z wydarzenia'
    TITLE = 'Tytuł'
    EDITOR = 'Redaktor'
    COVER = 'Zdjęcie okładki'
    LINK = 'Link'
    FILE = 'Plik'
    
class FieldEventSummaryContentContribution():
    VERBOSE_NAME = 'rola osoby we wkład treści'
    VERBOSE_NAME_PLURAL = 'role osoby we wkład treści'
    EVENT_SUMMARY = 'Sprawozdanie z wydarzenia'
    PERSON = 'Osoba'
    ROLE = 'Rola'
    
class FieldEventAuthorized():    
    VERBOSE_NAME = 'uprawnienia instytucji do wydarzenia'
    VERBOSE_NAME_PLURAL = 'uprawnienia instytucji do wydarzeń'
    AUTHORIZED = 'Uprawnienie'
    EVENT = 'Wydarzenie' 
        
class FieldEventModification():
    VERBOSE_NAME = 'modyfikacja wydarzenia'
    VERBOSE_NAME_PLURAL = 'modyfikacje wydarzenia'
    EVENT = 'Wydarzenie'
    USER = 'Użytkownik'
    DATE_TIME = 'Data i czas'

class FieldEventFilter():
    STATUS = 'Status'
    ONLY_MY = 'Tylko moje wydarzenia'
