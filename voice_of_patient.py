import os
import tempfile
import speech_recognition as sr
from pydub import AudioSegment
import requests
from io import BytesIO

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
apikeys_path = os.path.join(os.path.dirname(__file__), 'apikeys')
print(f"[PatientVoice] Loading API keys from: {apikeys_path}")
print(f"[PatientVoice] File exists: {os.path.exists(apikeys_path)}")
api_keys = read_api_keys(apikeys_path)
GROQ_API_KEY = api_keys.get('GROQ_API_KEY')
print(f"[PatientVoice] GROQ_API_KEY found: {GROQ_API_KEY is not None}")
print(f"[PatientVoice] GROQ_API_KEY length: {len(GROQ_API_KEY) if GROQ_API_KEY else 0}")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


class PatientVoice:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        # Adjust for ambient noise level
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.energy_threshold = 300  # Default energy threshold
        self.recognizer.pause_threshold = 0.8   # Shorter pause threshold for better responsiveness
        self.api_key = GROQ_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def transcribe_audio(self, audio_file_path):
        """Transcribe audio file to text using multiple recognition methods with fallbacks"""
        try:
            # Convert audio to WAV format if it's not already
            audio_file_path = self._ensure_wav_format(audio_file_path)
            
            # Load the audio file
            with sr.AudioFile(audio_file_path) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                # Record audio from the file
                audio_data = self.recognizer.record(source)
                
                # Try Google Speech Recognition first
              
                
                # If Google fails, try Whisper API via Groq as fallback
                if self.api_key:
                    try:
                        return self._transcribe_with_groq(audio_file_path)
                    except Exception as e:
                        print(f"Error with Groq API transcription: {str(e)}")
                
                # If all else fails, try Sphinx (offline recognition)
                
                    
                # If all methods fail
                return "Sorry, I couldn't understand what you said. Please try again."
                
        except Exception as e:
            print(f"Error transcribing audio: {str(e)}")
            return "An error occurred while processing your audio. Please try again."
    
    def _ensure_wav_format(self, audio_file_path):
        """Convert audio to WAV format if it's not already"""
        try:
            # Check if the file is already in WAV format
            if audio_file_path.lower().endswith('.wav'):
                return audio_file_path
            
            # Get the file extension
            file_ext = os.path.splitext(audio_file_path)[1].lower()
            
            # Convert to WAV if it's a supported format
            if file_ext in ['.mp3', '.ogg', '.flac', '.m4a', '.wma']:
                # Load the audio file
                audio = AudioSegment.from_file(audio_file_path, format=file_ext[1:])
                
                # Create a temporary WAV file
                temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
                temp_wav.close()
                
                # Export as WAV
                audio.export(temp_wav.name, format='wav')
                return temp_wav.name
            else:
                # If the format is not supported, return the original file
                print(f"Warning: Unsupported audio format {file_ext}. Attempting to process as is.")
                return audio_file_path
                
        except Exception as e:
            print(f"Error converting audio format: {str(e)}")
            return audio_file_path
    
    def _transcribe_with_groq(self, audio_file_path):
        """Transcribe audio using Groq API with Whisper model"""
        try:
            # Define the Groq API endpoint for audio transcription
            transcription_url = "https://api.groq.com/openai/v1/audio/transcriptions"
            
            # Read the audio file as binary data
            with open(audio_file_path, "rb") as audio_file:
                # Prepare the multipart form data
                files = {
                    "file": (os.path.basename(audio_file_path), audio_file, "audio/wav")
                }
                
                # Prepare the form data
                data = {
                    "model": "whisper-large-v3",  # Use Whisper model for transcription
                    "language": "en",  # Specify language (optional)
                    "response_format": "json"  # Get response in JSON format
                }
                
                # Make the API request
                response = requests.post(
                    transcription_url, 
                    headers={"Authorization": f"Bearer {self.api_key}"}, 
                    files=files,
                    data=data
                )
                response.raise_for_status()
                
                # Extract the transcription
                result = response.json()
                transcription = result.get("text", "")
                
                return transcription
            
        except Exception as e:
            print(f"Error with Groq API transcription: {str(e)}")
            raise
    
    def record_from_microphone(self, duration=5):
        """Record audio from microphone for specified duration"""
        try:
            # Create a temporary file to store the recording
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_file.close()
            
            # Record audio from microphone
            with sr.Microphone() as source:
                print("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                print(f"Recording for {duration} seconds...")
                audio_data = self.recognizer.record(source, duration=duration)
                
                # Save the recorded audio to the temporary file
                with open(temp_file.name, 'wb') as f:
                    f.write(audio_data.get_wav_data())
                
                return temp_file.name
                
        except Exception as e:
            print(f"Error recording from microphone: {str(e)}")
            return None
    
    def adjust_sensitivity(self, energy_threshold=None, pause_threshold=None):
        """Adjust the sensitivity of the speech recognizer"""
        if energy_threshold is not None:
            self.recognizer.energy_threshold = energy_threshold
        if pause_threshold is not None:
            self.recognizer.pause_threshold = pause_threshold