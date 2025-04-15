# AI Medical Chatbot with Vision and Voice

This project implements an AI medical assistant chatbot with multimodal capabilities, including text, voice, and image processing. The chatbot uses the Groq API with LLaMA 3.2 90B Vision for AI responses and the ElevenLabs API for natural-sounding voice output.

## Features

- **Text-based interaction**: Type your medical questions or describe symptoms
- **Voice input**: Speak directly to the AI using your microphone
- **Image analysis**: Upload images of visible symptoms for AI analysis
- **Natural voice responses**: Hear the AI doctor's responses in a natural-sounding voice
- **Location awareness**: Automatically detects patient location for more relevant medical advice
- **Hospital finder**: Find nearby hospitals and clinics using OpenStreetMap data
- **Modern UI**: Clean, responsive interface built with Gradio

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Groq API key (for LLaMA 3.2 90B Vision model)
- ElevenLabs API key (for text-to-speech)

### Installation

1. Clone this repository or download the files

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with your API keys:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
   ```

### Running the Application

Start the application by running:
```
python medical_chatbot.py
```

This will launch the Gradio web interface, typically at http://127.0.0.1:7860/

## Project Structure

- `brain_of_doctor.py`: Core AI logic using Groq API
- `voice_of_patient.py`: Speech-to-text functionality
- `voice_of_doctor.py`: Text-to-speech using ElevenLabs
- `location_service.py`: Location detection and nearby hospital finder using OpenStreetMap
- `medical_chatbot.py`: Web interface built with Gradio
- `requirements.txt`: Required Python packages

## Usage

1. **Text Input**: Type your medical question in the text box
2. **Voice Input**: Click the microphone button and speak your question
3. **Image Upload**: Upload an image of visible symptoms (optional)
4. **Get Response**: Click "Get Medical Advice" to receive the AI doctor's response
5. **Listen to Response**: Play the audio to hear the doctor's voice response
6. **Find Nearby Hospitals**: Ask questions like "What's the nearest hospital to me?" or "Find clinics near me" to get information about nearby medical facilities

## Important Note

This AI medical assistant is for informational purposes only and does not replace professional medical advice. Always consult with a healthcare professional for medical concerns.

## License

This project is licensed under the MIT License - see the LICENSE file for details.