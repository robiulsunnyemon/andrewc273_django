from django.core.management.base import BaseCommand
import json
import os
from django.conf import settings
from apps.resources.models import Prison


class Command(BaseCommand):
    help = 'Load prison data from JSON'

    def handle(self, *args, **kwargs):
        file_path = os.path.join(settings.BASE_DIR,  'prison.json')

        with open(file_path) as f:
            data = json.load(f)

        locations = data.get('Locations', [])

        for item in locations:
            Prison.objects.update_or_create(
                code=item.get('code'),
                defaults={
                    'name': item.get('name'),
                    'name_title': item.get('nameTitle'),
                    'name_display': item.get('nameDisplay'),
                    'type': item.get('type'),
                    'security_level': item.get('securityLevel'),
                    'region': item.get('region'),
                    'latitude': float(item.get('latitude') or 0),
                    'longitude': float(item.get('longitude') or 0),
                    'url': item.get('url'),
                    'time_zone': item.get('timeZone'),
                    'address': item.get('address'),
                    'city': item.get('city'),
                    'state': item.get('state'),
                    'zip_code': item.get('zipCode'),
                    'phone_number': item.get('phoneNumber'),
                    'contact_email': item.get('contactEmail'),
                    'gender': item.get('gender'),
                    'facl_type_description': item.get('faclTypeDescription'),
                    'has_camp': item.get('hasCamp', False),
                    'has_fsl': item.get('hasFsl', False),
                    'has_fdc': item.get('hasFdc', False),
                    'has_sff': item.get('hasSff', False),
                    'has_ihp': item.get('hasIhp', False),
                    'image_normal': item.get('imageNormal'),
                    'image_small': item.get('imageSmall'),
                }
            )

        self.stdout.write(self.style.SUCCESS(' Prison data imported successfully'))