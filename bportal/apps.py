from django.apps import AppConfig

class BportalAppConfig(AppConfig):
    name = 'bportal'
    label = 'bportal'
    verbose_name = "BPortal"
    
    def ready(self):
        import bportal.module.common.notifications
