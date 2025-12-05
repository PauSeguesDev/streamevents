from django.core.management.base import BaseCommand
from django.utils import timezone
from events.models import Event

class Command(BaseCommand):
    help = 'Updates the status of scheduled events to live if their start time has passed.'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        # Find scheduled events that should be live
        events_to_update = Event.objects.filter(status='scheduled', scheduled_date__lte=now)
        
        count = 0
        for event in events_to_update:
            if event.update_status():
                count += 1
                self.stdout.write(self.style.SUCCESS(f'Event "{event.title}" is now LIVE.'))
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No events needed updating.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Successfully updated {count} events.'))