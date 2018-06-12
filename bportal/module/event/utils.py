# -*- coding: utf-8 -*-
from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.db import models

from bportal.module.event.models import Event


class EventDay(models.Model):
    
    def __init__(self, d=datetime.now().date()):
        self.__day = d
        self.__events = list()
        self.__is_today = False
    
    def addEvent(self, e):
        self.__events.append(e)
        
    @property
    def day(self):
        return self.__day
    
    @property
    def events(self):
        return self.__events
    
    @property
    def is_today(self):
        return self.__day == datetime.today().date()
    
    class Meta:
        abstract = True
        
        
class EventMonth(models.Model):
    
    def __init__(self, m=datetime.today().date()):
        self.__month = m
        self.__events_days = list()
    
    @property
    def month(self):
        return self.__month
    
    @property
    def events_days(self):
        return self.__events_days
    
    def addEventDay(self, d):
        self.__events_days.append(d)
            
    class Meta:
        abstract = True
        
        
def get_events_calendar_before_first_day():
    months_backward = 2
    date_from = datetime.now().date() - relativedelta(months=months_backward)
    return date_from - relativedelta(days=1)


def get_events_calendar_after_last_day():
    months_forward = 3
    date_to = datetime.now().date() + relativedelta(months=months_forward)
    return date_to + relativedelta(days=1)

            
def get_events_calendar_list():
    months_backward = 2
    months_forward = 3
    date_from = datetime.now().date() - relativedelta(months=months_backward)
    date_to = datetime.now().date() + relativedelta(months=months_forward)
    
    events_list = Event.objects.filter(event_date_from__gte=date_from, event_date_from__lte=date_to, event_is_accepted = True).order_by('event_date_from','event_time_from')
    
    months_events_list = list()
    curr_date = date_from
    for i in range(months_backward + months_forward + 1):
        month_events = events_list.filter(event_date_from__year=curr_date.year, event_date_from__month=curr_date.month)
        em = EventMonth(curr_date)
        days = dict()
        curr_day = datetime(curr_date.year, curr_date.month, 1).date()
        while curr_day.month == curr_date.month:
            ed = EventDay(curr_day)
            days[curr_day.day] = ed
            em.addEventDay(ed)
            curr_day = curr_day+relativedelta(days=1)
            
        for ev in month_events:
            if ev.event_date_from.day not in days:
                ed = EventDay(ev.event_date_from)
                days[ev.event_date_from.day] = ed
                em.addEventDay(ed)
            else:
                ed = days[ev.event_date_from.day]
            ed.addEvent(ev)
        months_events_list.append(em)                
        curr_date = date_from+relativedelta(months=i+1)
    
    return months_events_list;
