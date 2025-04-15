import json
import requests
from typing import Dict, Optional
from config import FAST2SMS_API_KEY

class EmergencyService:
    def __init__(self):
        self.api_key = FAST2SMS_API_KEY
        self.contacts_file = "contacts.json"
        self._load_contacts()
    
    def _load_contacts(self) -> None:
        """Load emergency contacts from JSON file"""
        try:
            with open(self.contacts_file, "r") as f:
                self.contacts = json.load(f)
        except FileNotFoundError:
            self.contacts = {}
            self._save_contacts()
    
    def _save_contacts(self) -> None:
        """Save emergency contacts to JSON file"""
        with open(self.contacts_file, "w") as f:
            json.dump(self.contacts, f, indent=2)
    
    def get_emergency_contact(self, user_id: str) -> Optional[Dict]:
        """Get emergency contact for a user"""
        return self.contacts.get(user_id)
    
    def add_emergency_contact(self, user_id: str, name: str, phone: str) -> None:
        """Add or update emergency contact for a user"""
        self.contacts[user_id] = {
            "name": name,
            "phone": phone
        }
        self._save_contacts()
    
    def send_emergency_sms(self, name: str, location: Dict, phone: str) -> Dict:
        """Send emergency SMS using Fast2SMS API"""
        if not phone or not phone.isdigit() or len(phone) < 10:
            return {"error": "Invalid phone number", "status": "failed"}
            
        message = f"🚨 Emergency Alert!\n{name} needs immediate medical assistance in {location['city']}.\n📍 Location: {location['map_link']}"
        
        if len(message) > 160:  # SMS length limit
            message = message[:157] + "..."
        
        payload = {
            'sender_id': 'FSTSMS',
            'message': message,
            'language': 'english',
            'route': 'p',
            'numbers': phone,
        }
        
        headers = {
            'authorization': self.api_key,
            'Content-Type': "application/x-www-form-urlencoded",
            'Cache-Control': 'no-cache'
        }
        
        try:
            response = requests.post(
                "https://www.fast2sms.com/dev/bulkV2",
                data=payload,
                headers=headers,
                timeout=30  # Set timeout for the request
            )
            response_data = response.json()
            
            if response.status_code != 200:
                return {"error": "API request failed", "status": "failed", "details": response_data}
                
            return response_data
        except requests.Timeout:
            return {"error": "Request timed out", "status": "failed"}
        except requests.RequestException as e:
            return {"error": str(e), "status": "failed"}
        except Exception as e:
            return {"error": "Unexpected error: " + str(e), "status": "failed"}
    
    def format_location_for_sms(self, location: Dict) -> Dict:
        """Format location data for SMS message"""
        return {
            "city": location.get("city", "Unknown Location"),
            "map_link": f"https://www.google.com/maps?q={location.get('latitude', '')},{location.get('longitude', '')}"
        }