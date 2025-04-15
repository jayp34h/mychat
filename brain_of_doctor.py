import os
import base64
import requests
from emotion_detector import EmotionDetector

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
print(f"Loading API keys from: {apikeys_path}")
print(f"File exists: {os.path.exists(apikeys_path)}")
api_keys = read_api_keys(apikeys_path)
GROQ_API_KEY = api_keys.get('GROQ_API_KEY')
print(f"GROQ_API_KEY found: {GROQ_API_KEY is not None}")
print(f"GROQ_API_KEY length: {len(GROQ_API_KEY) if GROQ_API_KEY else 0}")

# Groq API endpoint
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

class DoctorBrain:
    def __init__(self):
        self.conversation_history = []
        self.headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        self.emotion_detector = EmotionDetector()
    def add_message_to_history(self, role, content, image_url=None):
        """Add a message to the conversation history"""
        if image_url:
            # For messages with images
            message = {
                "role": role,
                "content": [
                    {"type": "text", "text": content},
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url}
                    }
                ]
            }
        else:
            # For text-only messages
            message = {"role": role, "content": content}
        
        self.conversation_history.append(message)
    
    def get_initial_system_message(self):
        """Return the system message that defines the AI doctor's behavior"""
        system_content = "You are an AI medical assistant designed to provide helpful, accurate, and ethical medical information. \n\nGuidelines:\n1. Provide general medical information and first-aid advice when appropriate\n2. Always recommend consulting with a healthcare professional for diagnosis, treatment, or medical emergencies\n3. Maintain a compassionate, professional tone\n4. If you see an image, describe what you observe and provide relevant medical context\n5. Clearly state limitations of your advice and the importance of professional medical consultation\n6. Never claim to diagnose conditions definitively\n7. Prioritize patient safety above all else\n8. When location information is provided, consider regional health factors such as local disease prevalence, available healthcare facilities, and regional medical practices\n9. When patients ask about nearby hospitals or clinics, provide them with information about the closest medical facilities\n\nWhen analyzing images:\n- Describe visible symptoms objectively\n- Mention possible common causes for such symptoms\n- Provide general care recommendations\n- Emphasize the importance of professional medical evaluation\n\nWhen location data is available:\n- Consider regional health concerns or outbreaks in that area\n- Provide information about local healthcare resources when appropriate\n- Adjust recommendations based on geographic context\n- When asked about nearby hospitals or clinics, list the closest options with their distance, address, and contact information\n\nRemember that your advice is informational and does not replace professional medical care."
        return {"role": "system", "content": system_content}
    
    def encode_image(self, image_path):
        """Encode image to base64 string"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def get_response(self, user_input=None, image_path=None):
        """Get response from Groq API with emotion-aware responses"""
        # First, detect emotion if there's text input
        emotional_response = ""
        if user_input:
            emotional_response, detected_emotion = self.emotion_detector.get_response(user_input)
            # Add emotional context to the conversation
            user_input = f"[Patient's emotion appears to be {detected_emotion}] {user_input}"
        try:
            # Prepare messages for the API request
            messages = []
            
            # Handle different input scenarios
            if image_path:
                # For image processing (with or without text)
                try:
                    # Encode the image to base64
                    base64_image = self.encode_image(image_path)
                    
                    # Create user message based on whether text was provided
                    if user_input:
                        # Image + text input
                        user_message = {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": user_input},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                                }
                            ]
                        }
                    else:
                        # Image-only input (no automatic prompt generation)
                        user_message = {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                                }
                            ]
                        }
                    
                    # For image inputs, we need to add the system instructions as a user message first
                    # because Groq API doesn't support system messages with image inputs
                    system_content = self.get_initial_system_message()["content"]
                    messages.append({"role": "user", "content": system_content})
                    messages.append({"role": "assistant", "content": "I'll help you with your medical questions and image analysis according to these guidelines."})
                    messages.append(user_message)
                    
                except Exception as e:
                    return f"Error processing image: {str(e)}"
            else:
                # For text-only input
                system_message = self.get_initial_system_message()
                messages.append(system_message)
                messages.append({"role": "user", "content": user_input})
            
            # Prepare the request payload
            payload = {
                "model": "llama-3.2-90b-vision-preview",  # Using the vision model for both text and image
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1024
            }
            
            # Print debug info before making the request
            print(f"Making API request to: {GROQ_API_URL}")
            print(f"Using model: {payload['model']}")
            print(f"Auth header present: {self.headers.get('Authorization') is not None}")
            print(f"Number of messages: {len(messages)}")
            
            # Make the API request
            response = requests.post(GROQ_API_URL, headers=self.headers, json=payload)
            
            # Check response status
            print(f"API response status code: {response.status_code}")
            if response.status_code != 200:
                error_detail = response.text
                print(f"API error response: {error_detail}")
                return f"Error communicating with Groq API: Status {response.status_code} - {error_detail}"
                
            response.raise_for_status()
            
            # Extract the assistant's message
            result = response.json()
            assistant_message = result["choices"][0]["message"]["content"]
            
            # Store the successful conversation
            self.conversation_history = messages + [{
                "role": "assistant",
                "content": assistant_message
            }]
            
            # Combine emotional response with medical response if there's text input
            if emotional_response:
                combined_response = f"{emotional_response}\n\n{assistant_message}"
                return combined_response
            
            return assistant_message
        
        except requests.exceptions.RequestException as e:
            print(f"Request exception: {str(e)}")
            return f"Error communicating with Groq API: {str(e)}"
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return f"Unexpected error: {str(e)}"