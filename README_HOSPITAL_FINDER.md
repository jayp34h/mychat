# Hospital Finder Feature - myMedihelp

This document explains how to use the hospital finder feature in myMedihelp, which allows patients to find nearby hospitals and clinics based on their precise location.

## Overview

The hospital finder feature uses browser geolocation (more accurate than IP-based location) to find nearby medical facilities. It consists of:

1. A web interface for sharing location and viewing nearby hospitals
2. Integration with the medical chatbot to suggest using the web interface when hospital-related queries are detected
3. Backend API that uses OpenStreetMap's Overpass API to find hospitals and clinics

## Setup and Usage

### Prerequisites

Ensure you have all dependencies installed:

```
pip install -r requirements.txt
```

### Running the Application

1. Start the Flask web server:

```
python app.py
```

2. Access the hospital finder web interface at: http://localhost:5000/

3. Click the "Share My Location" button to allow the browser to access your precise location

4. View the list of nearby hospitals and clinics with details including:
   - Name
   - Distance (in kilometers)
   - Address
   - Phone number
   - Website (if available)

### Integration with Medical Chatbot

The medical chatbot (run with `python medical_chatbot.py`) will detect when users ask about nearby hospitals and suggest using the web interface for more accurate results.

Example queries that trigger this feature:
- "Where is the nearest hospital?"
- "Find me a clinic nearby"
- "I need the closest medical center"

## Technical Details

- The frontend uses the browser's Geolocation API for precise location data
- The backend uses OpenStreetMap's Overpass API to find hospitals and clinics
- Distance calculations use the Haversine formula to account for Earth's curvature
- CORS is enabled to allow cross-origin requests between the frontend and backend

## Troubleshooting

- If location permission is denied, check your browser settings and ensure location services are enabled
- If no hospitals are found, try increasing the search radius in the `find_nearby_hospitals` function
- For API rate limiting issues, consider implementing caching or using a different geocoding service