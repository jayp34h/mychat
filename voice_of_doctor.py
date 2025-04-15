import os
import tempfile
import requests
from gtts import gTTS

# Function to read API keys from file
def read_api_keys(file_path):
    api_keys = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    api_keys[key.strip()] = value.strip()
    except Exception as e:
        print(f"Error reading API keys: {str(e)}")
    return api_keys

# Read API keys from file
api_keys = read_api_keys(os.path.join(os.path.dirname(__file__), 'apikeys'))
ELEVENLABS_API_KEY = api_keys.get('ELEVENLABS_API_KEY')

class DoctorVoice:
    def __init__(self):
        self.api_key = ELEVENLABS_API_KEY
        self.base_url = "https://api.elevenlabs.io/v1"
        self.voice_id = "pNInz6obpgDQGcFmaJgB"  # Adam voice (professional male voice)
        self.headers = {
            "Accept": "audio/mpeg",
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def text_to_speech(self, text, output_path=None, use_google_tts=False):
        """Convert text to speech using ElevenLabs API or Google TTS as fallback"""
        # If use_google_tts is True or if ElevenLabs API key is not available, use Google TTS
        if use_google_tts or not self.api_key:
            return self.google_text_to_speech(text, output_path)
            
        try:
            # Prepare the request payload
            payload = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0.0,
                    "use_speaker_boost": True
                }
            }
            
            # Make the API request
            url = f"{self.base_url}/text-to-speech/{self.voice_id}"
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            
            # Save the audio to a file or return the audio data
            if output_path:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                return output_path
            else:
                # Create a temporary file
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                temp_file.write(response.content)
                temp_file.close()
                return temp_file.name
        
        except requests.exceptions.RequestException as e:
            print(f"Error communicating with ElevenLabs API: {str(e)}")
            print("Falling back to Google Text-to-Speech...")
            return self.google_text_to_speech(text, output_path)
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            print("Falling back to Google Text-to-Speech...")
            return self.google_text_to_speech(text, output_path)
            
    def google_text_to_speech(self, text, output_path=None):
        """Convert text to speech using Google Text-to-Speech"""
        try:
            # Create gTTS object
            tts = gTTS(text=text, lang='en', slow=False)
            
            # Save to file
            if output_path:
                tts.save(output_path)
                return output_path
            else:
                # Create a temporary file
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                temp_file.close()
                tts.save(temp_file.name)
                return temp_file.name
                
        except Exception as e:
            print(f"Error using Google Text-to-Speech: {str(e)}")
            return None
    
    def get_available_voices(self):
        """Get list of available voices from ElevenLabs"""
        try:
            url = f"{self.base_url}/voices"
            response = requests.get(url, headers={"xi-api-key": self.api_key})
            response.raise_for_status()
            
            voices = response.json()["voices"]
            return voices
        
        except requests.exceptions.RequestException as e:
            print(f"Error getting voices: {str(e)}")
            return []
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return []
    
    def set_voice(self, voice_id):
        """Set the voice to use for text-to-speech"""
        self.voice_id = voice_id