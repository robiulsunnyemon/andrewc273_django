import os
import re
import json
import time
import hashlib
import requests

def main():
    txt_path = os.path.join('apps', 'resources', 'data', 'halfway_houses.txt')
    json_path = os.path.join('apps', 'resources', 'data', 'halfway_houses.json')
    
    if not os.path.exists(txt_path):
        print(f"Error: {txt_path} not found.")
        return

    # 1. Parse halfway_houses.txt
    with open(txt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    raw_blocks = re.split(r'\n\s*\n', content)
    blocks = []
    for rb in raw_blocks:
        lines = [l.strip() for l in rb.splitlines() if l.strip()]
        lines = [l for l in lines if l != 'DIRECTORY OF ACTIVE CONTRACTS' and not l.startswith('(c) www.FedCURE.org') and not l.startswith('Note:')]
        if lines:
            blocks.append(lines)

    cs_regex = re.compile(r'^([^,]+),\s*([A-Z]{2})\s+(\d{5}(?:-\d{4})?)$')
    phone_regex = re.compile(r'(?:PHONE:\s*)?(\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4})', re.IGNORECASE)

    parsed_houses = []

    for lines in blocks:
        # Check if state header
        if len(lines) == 1 and lines[0].isupper() and ',' not in lines[0] and not phone_regex.search(lines[0]):
            continue

        cs_idx = -1
        cs_match = None
        for idx, line in enumerate(lines):
            m = cs_regex.match(line)
            if m:
                cs_idx = idx
                cs_match = m
                break

        if cs_idx == -1:
            continue

        city = cs_match.group(1).strip()
        state = cs_match.group(2).strip()
        zip_code = cs_match.group(3).strip()

        name = lines[0]
        address_lines = lines[1:cs_idx]

        if len(address_lines) > 0 and (name.endswith('&') or name.upper().endswith('AND') or (name.count('(') > name.count(')'))):
            name = name + ' ' + address_lines[0]
            address_lines = address_lines[1:]

        address_street = ", ".join(address_lines)
        if address_street:
            full_address = f"{address_street}, {city}, {state} {zip_code}"
        else:
            full_address = f"{city}, {state} {zip_code}"

        phone_number = ''
        if cs_idx + 1 < len(lines):
            phone_line = lines[cs_idx + 1]
            phone_m = phone_regex.search(phone_line)
            if phone_m:
                phone_number = phone_m.group(1).strip()
            else:
                phone_number = phone_line.replace('PHONE:', '').replace('phone:', '').strip()

        # Deterministic stable code
        unique_str = f"{name}-{city}-{state}".lower()
        code = f"LOC-{hashlib.md5(unique_str.encode('utf-8')).hexdigest()[:8].upper()}"

        parsed_houses.append({
            'code': code,
            'name': name,
            'nameTitle': name,
            'nameDisplay': name,
            'type': 'HALFWAY_HOUSE',
            'securityLevel': 'Minimum',
            'latitude': None,
            'longitude': None,
            'address': full_address,
            'city': city,
            'state': state,
            'zipCode': zip_code,
            'phoneNumber': phone_number,
            'faclTypeDescription': 'Residential Reentry Center'
        })

    print(f"Parsed {len(parsed_houses)} halfway houses from text file.")

    # 2. Load existing json data if available (to resume geocoding)
    existing_coords = {}
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                for item in existing_data.get('Locations', []):
                    if item.get('latitude') is not None and item.get('longitude') is not None:
                        existing_coords[item['code']] = (item['latitude'], item['longitude'])
            print(f"Loaded {len(existing_coords)} already geocoded houses from existing JSON.")
        except Exception as e:
            print(f"Warning: Could not read existing JSON file: {e}")

    # 3. Geocode with Nominatim API
    headers = {'User-Agent': 'AndrewC273App/1.0'}
    
    updated_count = 0
    for idx, house in enumerate(parsed_houses):
        code = house['code']
        if code in existing_coords:
            house['latitude'], house['longitude'] = existing_coords[code]
            continue

        full_addr = house['address']
        print(f"[{idx+1}/{len(parsed_houses)}] Geocoding: {full_addr}")
        
        lat, lon = None, None
        try:
            r = requests.get(
                'https://nominatim.openstreetmap.org/search',
                params={'q': full_addr, 'format': 'json', 'limit': 1},
                headers=headers,
                timeout=10
            )
            time.sleep(1.0) # Rate limit respect
            
            if r.status_code == 200:
                data = r.json()
                if data:
                    lat = float(data[0]['lat'])
                    lon = float(data[0]['lon'])
                    print(f"  Success: {lat}, {lon}")
                else:
                    # Fallback to City, State
                    fallback_q = f"{house['city']}, {house['state']}"
                    print(f"  No direct match. Trying fallback: {fallback_q}")
                    r_fb = requests.get(
                        'https://nominatim.openstreetmap.org/search',
                        params={'q': fallback_q, 'format': 'json', 'limit': 1},
                        headers=headers,
                        timeout=10
                    )
                    time.sleep(1.0)
                    if r_fb.status_code == 200:
                        data_fb = r_fb.json()
                        if data_fb:
                            lat = float(data_fb[0]['lat'])
                            lon = float(data_fb[0]['lon'])
                            print(f"  Success (fallback): {lat}, {lon}")
                        else:
                            print(f"  Warning: Fallback failed for {fallback_q}")
                    else:
                        print(f"  Warning: Fallback request failed with status {r_fb.status_code}")
            else:
                print(f"  Warning: Request failed with status {r.status_code}")
        except Exception as e:
            print(f"  Error during geocoding: {e}")
            time.sleep(2.0) # sleep slightly longer on error

        house['latitude'] = lat
        house['longitude'] = lon
        updated_count += 1
        
        # Save incrementally every 10 geocoded items to avoid losing progress
        if updated_count > 0 and updated_count % 10 == 0:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump({'Locations': parsed_houses}, f, indent=2)
            print(f"Saved progress to JSON file ({updated_count} new geocoded).")

    # 4. Final write
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({'Locations': parsed_houses}, f, indent=2)
    print(f"Finished! Written all halfway houses to {json_path}")

if __name__ == '__main__':
    main()
