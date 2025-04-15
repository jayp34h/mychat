import os
import requests

# Function to read API keys from file
def read_api_keys(file_path):
    api_keys = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    api_keys[key.strip()] = value.strip()
                    print(f"Found key: {key.strip()} with value length: {len(value.strip())}")
    except Exception as e:
        print(f"Error reading API keys: {str(e)}")
    return api_keys

# Get the absolute path to the apikeys file
apikeys_path = os.path.join(os.path.dirname(__file__), 'apikeys')
print(f"Looking for apikeys file at: {apikeys_path}")
print(f"File exists: {os.path.exists(apikeys_path)}")

# Read API keys from file
api_keys = read_api_keys(apikeys_path)
GROQ_API_KEY = api_keys.get('GROQ_API_KEY')
print(f"GROQ_API_KEY found: {GROQ_API_KEY is not None}")
print(f"GROQ_API_KEY length: {len(GROQ_API_KEY) if GROQ_API_KEY else 0}")

# Test the API key with a simple request
if GROQ_API_KEY:
    print("\nTesting GROQ API key with a simple request...")
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Simple test payload
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, how are you?"}
        ],
        "temperature": 0.7,
        "max_tokens": 50
    }
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions", 
            headers=headers, 
            json=payload
        )
        
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print("API key is valid!")
            print(f"Response: {response.json()['choices'][0]['message']['content']}")
        else:
            print(f"API key validation failed: {response.text}")
    except Exception as e:
        print(f"Error testing API key: {str(e)}")
else:
    print("No GROQ API key found in the apikeys file.")