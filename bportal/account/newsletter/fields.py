# -*- coding: utf-8 -*-
class FieldNewsletter():
    VERBOSE_NAME = 'Newsletter użytkownika'
    VERBOSE_NAME_PLURAL = 'Newslettery użytkowników'
    PERIOD = 'Częstotliwość otrzymywania newslettera'
    ARTICLE = 'Artykuły i wywiady'
    JOURNAL = 'Czasopisma'
    BOOK = 'Nowości wydawnicze'
    PROJECT = 'Projekty badawcze'
    DISSERTATION = 'Prace doktorskie'
    COMPETITION = 'Konkursy'
    JOBOFFER = 'Oferty pracy'
    EDUOFFER = 'Oferty edukacyjne'
    SCHOLARSHIP = 'Stypendia'
    EVENT_CATEGORIES = "Kategorie wydarzeń"
    NEW_CATEGORIES = "Kategorie aktualności"
    LAST_SENT = 'Ostatnio wysłany'
    UUID = 'UUID'
    NEWSLETTER_FLAG = "NEWSLETTER_FLAG"
    
class FieldManagementEmail():
    VERBOSE_NAME = 'Newsletter email - konfiguracja'
    VERBOSE_NAME_PLURAL = 'Newsletter email - konfiguracja'
    TITLE = 'Tytuł wiadomości'
    MESSAGE = 'Treść wiadomości'
    

class FieldNewsletterCustomContent():
    VERBOSE_NAME = 'Newsletter - treść'
    VERBOSE_NAME_PLURAL = 'Newsletter - treści'
    TITLE = 'Tytuł'
    MESSAGE = 'Wiadomość'
    VALID_SINCE = 'Ważna od'
    VALID_UNTIL = 'Ważna do'
    