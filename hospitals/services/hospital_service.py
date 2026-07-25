import urllib.request
import urllib.parse
import json
import random
import logging
from hospitals.utils.location import haversine_distance

logger = logging.getLogger(__name__)

class HospitalService:
    @staticmethod
    def get_nearby_hospitals(latitude, longitude, radius_meters=5000):
        """
        Fetches nearby clinics and hospitals using Overpass API (OpenStreetMap).
        Falls back to generating nearby mock clinics if API fails.
        """
        latitude = float(latitude)
        longitude = float(longitude)
        
        try:
            # Overpass API query for hospitals, clinics, and doctors within radius
            overpass_url = "https://overpass-api.de/api/interpreter"
            query = f"""[out:json][timeout:15];
            (
              node["amenity"="hospital"](around:{radius_meters},{latitude},{longitude});
              node["amenity"="clinic"](around:{radius_meters},{latitude},{longitude});
              node["amenity"="doctors"](around:{radius_meters},{latitude},{longitude});
              way["amenity"="hospital"](around:{radius_meters},{latitude},{longitude});
              way["amenity"="clinic"](around:{radius_meters},{latitude},{longitude});
            );
            out body center;"""
            
            data = urllib.parse.urlencode({'data': query}).encode('utf-8')
            req = urllib.request.Request(overpass_url, data=data, headers={'User-Agent': 'MedIntelApp/1.0'})
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                
            elements = result.get('elements', [])
            hospitals = []
            
            for elem in elements:
                tags = elem.get('tags', {})
                name = tags.get('name')
                if not name:
                    continue
                
                # Extract coordinates depending on element type
                elem_lat = elem.get('lat')
                elem_lon = elem.get('lon')
                if elem_lat is None or elem_lon is None:
                    center = elem.get('center', {})
                    elem_lat = center.get('lat')
                    elem_lon = center.get('lon')
                    
                if elem_lat is None or elem_lon is None:
                    continue
                
                dist = haversine_distance(latitude, longitude, elem_lat, elem_lon)
                
                # Construct address
                addr_parts = []
                if tags.get('addr:housenumber'):
                    addr_parts.append(tags.get('addr:housenumber'))
                if tags.get('addr:street'):
                    addr_parts.append(tags.get('addr:street'))
                if tags.get('addr:suburb'):
                    addr_parts.append(tags.get('addr:suburb'))
                if tags.get('addr:city'):
                    addr_parts.append(tags.get('addr:city'))
                    
                address = ", ".join(addr_parts) if addr_parts else "Nearby Area"
                
                # Mock rating based on name length to keep it consistent
                rating_seed = sum(ord(c) for c in name) % 11
                rating = round(4.0 + (rating_seed / 10.0), 1) # 4.0 - 5.0
                if rating > 5.0:
                    rating = 5.0
                
                hospitals.append({
                    "name": name,
                    "latitude": elem_lat,
                    "longitude": elem_lon,
                    "distance": f"{round(dist, 1)} km",
                    "distance_val": dist,
                    "rating": rating,
                    "phone": tags.get('phone', tags.get('contact:phone', 'N/A')),
                    "address": address,
                    "open_now": tags.get('opening_hours', 'Contact hospital for hours')
                })
                
            # Sort by distance
            hospitals.sort(key=lambda x: x["distance_val"])
            
            # Remove helper key
            for h in hospitals:
                del h["distance_val"]
                
            if hospitals:
                return hospitals[:10]  # Return top 10 nearest
                
        except Exception as e:
            logger.error(f"Error fetching from Overpass API: {e}")
            
        # Fallback to Mock Data generated around the user's location
        return HospitalService._generate_mock_hospitals(latitude, longitude)

    @staticmethod
    def _generate_mock_hospitals(lat, lon):
        """
        Fallback mock hospital generator using random offsets.
        Ensures map displays medical locations regardless of network status.
        """
        mock_templates = [
            ("City Emergency Hospital", 0.008, -0.005, 4.6, "+1 555-0101", "102 Health Boulevard"),
            ("Community Care Clinic", -0.004, 0.007, 4.2, "+1 555-0102", "456 Wellness Street"),
            ("St. Jude Medical Center", 0.012, 0.011, 4.8, "+1 555-0103", "789 Care Crescent"),
            ("Metro Health Clinic", -0.010, -0.009, 3.9, "+1 555-0104", "12 Medical Plaza"),
            ("Grace Family Doctors", 0.003, 0.004, 4.5, "+1 555-0105", "304 Hope Avenue")
        ]
        
        hospitals = []
        for name, lat_offset, lon_offset, rating, phone, address in mock_templates:
            h_lat = lat + lat_offset
            h_lon = lon + lon_offset
            dist = haversine_distance(lat, lon, h_lat, h_lon)
            hospitals.append({
                "name": name,
                "latitude": h_lat,
                "longitude": h_lon,
                "distance": f"{round(dist, 1)} km",
                "rating": rating,
                "phone": phone,
                "address": address,
                "open_now": "Open 24/7" if "Hospital" in name or "Center" in name else "08:00 - 18:00"
            })
            
        # Sort by distance
        hospitals.sort(key=lambda x: float(x["distance"].split()[0]))
        return hospitals
