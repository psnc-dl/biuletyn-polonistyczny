# -*- coding: utf-8 -*-
import logging
from django.core.management.base import BaseCommand
from bportal.newsletter.tools import NewsletterSender

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    args = ''
    help = 'prepare newsletters files for all users'

    def sendFiles(self):
        ns = NewsletterSender()
        ns.sendNewsEmails()
    
    def handle(self, *args, **options):
        logger.info('Sending newsletters files...')
        self.sendFiles()
        logger.info('Sending newsletters files done')