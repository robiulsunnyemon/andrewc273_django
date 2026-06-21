document.addEventListener('DOMContentLoaded', function() {
    const latInput = document.getElementById('id_latitude');
    const lngInput = document.getElementById('id_longitude');

    if (!latInput || !lngInput) {
        return;
    }

    // Create wrapper container for map and search
    const mapWrapper = document.createElement('div');
    mapWrapper.style.margin = '20px 0';
    mapWrapper.style.padding = '15px';
    mapWrapper.style.background = '#f8f9fa';
    mapWrapper.style.borderRadius = '8px';
    mapWrapper.style.border = '1px solid #e9ecef';

    // Create Search Bar
    const searchContainer = document.createElement('div');
    searchContainer.style.display = 'flex';
    searchContainer.style.gap = '10px';
    searchContainer.style.marginBottom = '15px';

    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.placeholder = 'Search address or facility name (e.g. Atlanta FCI)...';
    searchInput.style.flex = '1';
    searchInput.style.padding = '8px 12px';
    searchInput.style.border = '1px solid #ced4da';
    searchInput.style.borderRadius = '4px';
    searchInput.style.color = '#333';
    searchInput.style.fontSize = '14px';

    const searchButton = document.createElement('button');
    searchButton.type = 'button';
    searchButton.textContent = 'Search on Map';
    searchButton.style.padding = '8px 16px';
    searchButton.style.background = '#005177';
    searchButton.style.color = '#ffffff';
    searchButton.style.border = 'none';
    searchButton.style.borderRadius = '4px';
    searchButton.style.cursor = 'pointer';
    searchButton.style.fontSize = '14px';
    searchButton.style.fontWeight = 'bold';

    searchContainer.appendChild(searchInput);
    searchContainer.appendChild(searchButton);
    mapWrapper.appendChild(searchContainer);

    // Create Map Container
    const mapContainer = document.createElement('div');
    mapContainer.id = 'django-admin-leaflet-map';
    mapContainer.style.height = '350px';
    mapContainer.style.width = '100%';
    mapContainer.style.borderRadius = '6px';
    mapContainer.style.border = '1px solid #ced4da';
    mapContainer.style.zIndex = '1';
    mapWrapper.appendChild(mapContainer);

    // Help Text
    const helpText = document.createElement('p');
    helpText.textContent = '💡 Click on the map to manually place the marker, or use the search box to find a location.';
    helpText.style.margin = '10px 0 0 0';
    helpText.style.fontSize = '12px';
    helpText.style.color = '#6c757d';
    mapWrapper.appendChild(helpText);

    // Insert wrapper before the latitude field container
    const latFieldRow = latInput.closest('.form-row') || latInput.closest('.field-box') || latInput.parentElement;
    latFieldRow.parentNode.insertBefore(mapWrapper, latFieldRow);

    // Initialize Map
    let initialLat = parseFloat(latInput.value);
    let initialLng = parseFloat(lngInput.value);
    const defaultCenter = [37.0902, -95.7129]; // US Center
    const defaultZoom = 4;

    const hasValidCoords = !isNaN(initialLat) && !isNaN(initialLng) && initialLat !== 0 && initialLng !== 0;
    const center = hasValidCoords ? [initialLat, initialLng] : defaultCenter;
    const zoom = hasValidCoords ? 12 : defaultZoom;

    const map = L.map('django-admin-leaflet-map').setView(center, zoom);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    let marker;
    if (hasValidCoords) {
        marker = L.marker([initialLat, initialLng]).addTo(map);
    }

    // Map Click Handler
    map.on('click', function(e) {
        const lat = e.latlng.lat;
        const lng = e.latlng.lng;

        if (marker) {
            marker.setLatLng(e.latlng);
        } else {
            marker = L.marker(e.latlng).addTo(map);
        }

        latInput.value = lat.toFixed(6);
        lngInput.value = lng.toFixed(6);
    });

    // Nominatim Geocoding Search
    function performSearch() {
        const query = searchInput.value.trim();
        if (!query) return;

        searchButton.disabled = true;
        searchButton.textContent = 'Searching...';

        fetch(`https://nominatim.openstreetmap.org/search?format=json&limit=1&q=${encodeURIComponent(query)}`, {
            headers: {
                'Accept': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data && data.length > 0) {
                const result = data[0];
                const lat = parseFloat(result.lat);
                const lon = parseFloat(result.lon);

                map.setView([lat, lon], 14);

                if (marker) {
                    marker.setLatLng([lat, lon]);
                } else {
                    marker = L.marker([lat, lon]).addTo(map);
                }

                latInput.value = lat.toFixed(6);
                lngInput.value = lon.toFixed(6);
            } else {
                alert('Location not found. Please try a different query.');
            }
        })
        .catch(err => {
            console.error('Geocoding error:', err);
            alert('An error occurred while searching for the location.');
        })
        .finally(() => {
            searchButton.disabled = false;
            searchButton.textContent = 'Search on Map';
        });
    }

    searchButton.addEventListener('click', performSearch);
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            performSearch();
        }
    });

    // Sync input field edits back to map
    function updateMapFromInputs() {
        const lat = parseFloat(latInput.value);
        const lng = parseFloat(lngInput.value);

        if (!isNaN(lat) && !isNaN(lng)) {
            const latlng = [lat, lng];
            map.setView(latlng, map.getZoom());
            if (marker) {
                marker.setLatLng(latlng);
            } else {
                marker = L.marker(latlng).addTo(map);
            }
        }
    }

    latInput.addEventListener('change', updateMapFromInputs);
    lngInput.addEventListener('change', updateMapFromInputs);
});
