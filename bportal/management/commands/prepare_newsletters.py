# -*- coding: utf-8 -*-
import logging
from django.core.management.base import BaseCommand
from bportal.newsletter.tools import NewsletterGenerator

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    args = ''
    help = 'prepare newsletters files for all users'

    def prepareFiles(self):
        ng = NewsletterGenerator()
        ng.generateNewsPdfForAllUsers()
    
    def handle(self, *args, **options):
        logger.info('Preparing newsletters files...')
        self.prepareFiles()
        logger.info('Preparing newsletters files done')
