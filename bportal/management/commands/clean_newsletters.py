# -*- coding: utf-8 -*-
import logging
from django.core.management.base import BaseCommand
from bportal.newsletter.tools import NewsletterGenerator

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    args = ''
    help = 'delete newsletters files for all users'

    def deleteFiles(self):
        ng = NewsletterGenerator()
        ng.cleanAllNewsPdfs()
    
    def handle(self, *args, **options):
        logger.info('Cleaning newsletters files...')
        self.deleteFiles()
        logger.info('Cleaning newsletters files done')
