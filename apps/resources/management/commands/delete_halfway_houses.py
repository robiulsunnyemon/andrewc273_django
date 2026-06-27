from django.core.management.base import BaseCommand
from apps.resources.models import Prison

class Command(BaseCommand):
    help = 'Delete all halfway house records from the database'

    def handle(self, *args, **options):
        queryset = Prison.objects.filter(type='HALFWAY_HOUSE')
        count = queryset.count()
        
        self.stdout.write(f"Found {count} halfway house records to delete.")
        
        if count > 0:
            deleted_count, _ = queryset.delete()
            self.stdout.write(self.style.SUCCESS(f"Successfully deleted {deleted_count} halfway house records."))
        else:
            self.stdout.write(self.style.WARNING("No halfway house records found to delete."))
