# -*- coding: utf-8 -*-
from haystack.signals import RealtimeSignalProcessor
 
class BportalRealtimeSignalProcessor(RealtimeSignalProcessor):
    
    def handle_save(self, sender, instance, **kwargs):
        if hasattr(instance, 'is_imported') and instance.is_imported:
            return None
        return super(BportalRealtimeSignalProcessor, self).handle_save(sender, instance, **kwargs)
    
    def handle_delete(self, sender, instance, **kwargs):
        if hasattr(instance, 'is_imported') and instance.is_imported:
            return None
        return super(BportalRealtimeSignalProcessor, self).handle_delete(sender, instance, **kwargs)