import os
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.resources.models import Prison

class Command(BaseCommand):
    help = 'Load halfway house locations from a raw JSON file'

    def handle(self, *args, **options):
        file_path = os.path.join(settings.BASE_DIR, 'apps', 'resources', 'data', 'halfway_houses.json')
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"File not found at {file_path}"))
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        locations = data.get('Locations', [])

        created_count = 0
        updated_count = 0

        for item in locations:
            obj, created = Prison.objects.update_or_create(
                code=item.get('code'),
                defaults={
                    'name': item.get('name'),
                    'name_title': item.get('nameTitle'),
                    'name_display': item.get('nameDisplay'),
                    'type': 'HALFWAY_HOUSE',
                    'security_level': item.get('securityLevel', 'Minimum'),
                    'latitude': item.get('latitude'),
                    'longitude': item.get('longitude'),
                    'address': item.get('address'),
                    'city': item.get('city'),
                    'state': item.get('state'),
                    'zip_code': item.get('zipCode'),
                    'phone_number': item.get('phoneNumber'),
                    'facl_type_description': item.get('faclTypeDescription', 'Residential Reentry Center'),
                }
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully loaded halfway houses. Created: {created_count}, Updated: {updated_count}"))

