# -*- coding: utf-8 -*-
class FieldUserProfile():
    VERBOSE_NAME = 'profil użytkownika'
    VERBOSE_NAME_PLURAL = 'profile użytkownika'
    INSTITUTION = 'Instytucja'
    IS_EDITOR = 'Redaktor'
    PHOTO = 'Zdjęcie'
    NICK = 'Nick'
    BORN_DATE = 'Data urodzenia'
    PHONE = 'Telefon'
    PERSON = 'Osoba w bazie'
    NOTIFICATIONS = 'Powiadomienia email'
    DAYS_BEFORE_EVENT = 'Dni przed wydarzeniem'
    NEWSLETTER = 'Newsletter'
    ITEMS_PER_PAGE = 'Ilość pozycji na stronie wyników'
    NEWSLETTER_PERIOD = 'Częstotliwość otrzymywania newslettera'
    USER_NEWSLETTER_FLAG = 'Subskrypcja newslettera'
    LAST_EDIT_DATE_TIME = 'Ostatnia zmiana'    
    UUID = 'UUID'
    INSTITUTIONS_EDITOR = 'Redaktor instytucji'
    
class FieldPersonalDataProfile():
    NICK = 'Nick'
    FIRST_NAME = 'Imię'
    LAST_NAME = 'Nazwisko'
    EMAIL = 'Adres email'
    BORN_DATE = 'Data urodzenia'
    PHONE = 'Telefon'

class FieldPasswordProfile():
    USERNAME = 'Login'
    PASSWORD = 'Hasło'
    PASSWORD_REPEATED = 'Powtórz hasło'
    
class FieldPhotoProfile():
    NEW_PHOTO = 'Nowe zdjęcie'
    REMOVE_PHOTO = 'Usuń zdjęcie'
