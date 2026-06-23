import os
import re
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.resources.models import Prison

class Command(BaseCommand):
    help = 'Load halfway house locations from a raw text file'

    def handle(self, *args, **options):
        file_path = os.path.join(settings.BASE_DIR, 'apps', 'resources', 'data', 'halfway_houses.txt')
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"File not found at {file_path}"))
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split content into blocks by double newlines or similar blank lines
        raw_blocks = re.split(r'\n\s*\n', content)
        
        # Clean blocks
        blocks = []
        for rb in raw_blocks:
            lines = [l.strip() for l in rb.splitlines() if l.strip()]
            # Filter out headers and copyright
            lines = [l for l in lines if l != 'DIRECTORY OF ACTIVE CONTRACTS' and not l.startswith('(c) www.FedCURE.org') and not l.startswith('Note:')]
            if lines:
                blocks.append(lines)

        cs_regex = re.compile(r'^([^,]+),\s*([A-Z]{2})\s+(\d{5}(?:-\d{4})?)$')
        phone_regex = re.compile(r'(?:PHONE:\s*)?(\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4})', re.IGNORECASE)

        created_count = 0
        updated_count = 0

        for lines in blocks:
            # Check if this block is a state header (1 line of all uppercase letters, no commas)
            if len(lines) == 1 and lines[0].isupper() and ',' not in lines[0] and not phone_regex.search(lines[0]):
                # It's a state header (like "ALASKA" or "WEST VIRGINIA"), skip it
                continue

            # Find the line that matches City, State Zip
            cs_idx = -1
            cs_match = None
            for idx, line in enumerate(lines):
                m = cs_regex.match(line)
                if m:
                    cs_idx = idx
                    cs_match = m
                    break

            if cs_idx == -1:
                # If we can't find a city, state, zip pattern, skip
                self.stdout.write(self.style.WARNING(f"Skipping unparseable block: {lines}"))
                continue

            city = cs_match.group(1).strip()
            state = cs_match.group(2).strip()
            zip_code = cs_match.group(3).strip()

            # Name and street address lines before cs_idx
            name = lines[0]
            address_lines = lines[1:cs_idx]

            # If the first line ends with open parenthesis or '&' or 'AND', join it with the next line for the name
            if len(address_lines) > 0 and (name.endswith('&') or name.upper().endswith('AND') or (name.count('(') > name.count(')'))):
                name = name + ' ' + address_lines[0]
                address_lines = address_lines[1:]

            address = ", ".join(address_lines)
            if address:
                full_address = f"{address}, {city}, {state} {zip_code}"
            else:
                full_address = f"{city}, {state} {zip_code}"

            # Phone number is usually after cs_idx
            phone_number = ''
            if cs_idx + 1 < len(lines):
                phone_line = lines[cs_idx + 1]
                phone_m = phone_regex.search(phone_line)
                if phone_m:
                    phone_number = phone_m.group(1).strip()
                else:
                    # Clean potential label
                    phone_number = phone_line.replace('PHONE:', '').replace('phone:', '').strip()

            # Create or update the record
            obj, created = Prison.objects.update_or_create(
                name=name,
                city=city,
                state=state,
                type='HALFWAY_HOUSE',
                defaults={
                    'name_title': name,
                    'name_display': name,
                    'address': full_address,
                    'zip_code': zip_code,
                    'phone_number': phone_number,
                    'security_level': 'Minimum',
                    'facl_type_description': 'Residential Reentry Center',
                }
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully loaded halfway houses. Created: {created_count}, Updated: {updated_count}"))
