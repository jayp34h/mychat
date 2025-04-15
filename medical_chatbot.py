import os
import tempfile
import gradio as gr
import requests
from brain_of_doctor import DoctorBrain
from voice_of_patient import PatientVoice
from voice_of_doctor import DoctorVoice
from location_service import get_user_location, find_nearby_hospitals, format_hospital_results

# Initialize components
doctor_brain = DoctorBrain()
patient_voice = PatientVoice()
doctor_voice = DoctorVoice()

# Custom CSS for modern UI
custom_css = """
/* Generate Report button */
.generate-report-btn {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 9999;
    padding: 10px 16px;
    background-color: #2563EB;
    color: white;
    border: none;
    border-radius: 20px;
    font-weight: bold;
    cursor: pointer;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    transition: background-color 0.3s ease;
    text-decoration: none;
    display: flex;
    align-items: center;
    gap: 8px;
}

.generate-report-btn:hover {
    background-color: #1E40AF;
}

/* Base styles */
:root {
    --primary-color: #3b82f6;
    --secondary-color: #1e40af;
    --background-color: #f8fafc;
    --text-color: #1e293b;
    --border-color: #e2e8f0;
    --shadow-color: rgba(0, 0, 0, 0.1);
}

/* Floating Generate Report button */
.generate-report-btn {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 9999;
    padding: 10px 16px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 20px;
    font-weight: bold;
    cursor: pointer;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    transition: background-color 0.3s ease;
    text-decoration: none;
    display: flex;
    align-items: center;
    gap: 8px;
}

.generate-report-btn:hover {
    background-color: #0056b3;
}

/* Auth button styles */

/* Success message styling */
.success-message {
    background-color: #ecfdf5;
    color: #047857;
    border-radius: 8px;
    padding: 1rem;
    margin-top: 1rem;
    border-left: 4px solid #10b981;
    font-weight: 500;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    text-align: center;
    animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}

:root {
    --primary-color: #3b82f6;
    --secondary-color: #1e40af;
    --background-color: #f8fafc;
    --text-color: #1e293b;
    --border-color: #e2e8f0;
    --shadow-color: rgba(0, 0, 0, 0.1);
}

.gradio-container {
    background-color: var(--background-color);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.main-header {
    text-align: center;
    color: var(--secondary-color);
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 1.5rem;
    padding-top: 1.5rem;
}

.sub-header {
    text-align: center;
    color: var(--text-color);
    font-size: 1.2rem;
    margin-bottom: 2rem;
}

.input-container, .output-container {
    border-radius: 12px;
    border: 1px solid var(--border-color);
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    background-color: white;
    box-shadow: 0 4px 6px var(--shadow-color);
}

.input-label, .output-label {
    font-weight: 600;
    color: var(--secondary-color);
    margin-bottom: 0.5rem;
}

.submit-btn {
    background-color: var(--primary-color) !important;
    color: white !important;
    border-radius: 8px !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}

.submit-btn:hover {
    background-color: var(--secondary-color) !important;
    transform: translateY(-2px);
}

.audio-player {
    border-radius: 8px;
    overflow: hidden;
    margin-top: 1rem;
}

.image-upload {
    border: 2px dashed var(--border-color);
    border-radius: 8px;
    padding: 1rem;
    text-align: center;
}

.response-area {
    background-color: #f1f5f9;
    border-radius: 8px;
    padding: 1rem;
    margin-top: 1rem;
    max-height: 300px;
    overflow-y: auto;
}

.footer {
    text-align: center;
    margin-top: 2rem;
    color: var(--text-color);
    font-size: 0.9rem;
}

/* Location button styling */
.location-btn {
    background-color: var(--primary-color) !important;
    color: white !important;
    border-radius: 8px !important;
    padding: 0.5rem 1rem !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    margin-top: 0.5rem !important;
    cursor: pointer !important;
}

.location-btn:hover {
    background-color: var(--secondary-color) !important;
    transform: translateY(-2px);
}

.location-status {
    margin-top: 0.5rem;
    font-size: 0.9rem;
    color: var(--text-color);
}


"""

# JavaScript for location sharing and SOS functionality
location_js = """
<script>
// Function to get user's location
function getLocation() {
    document.getElementById('status').innerText = "Requesting your location...";
    
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;

                // Store the location data directly in the hidden input field
                document.getElementById("status").innerText = "✅ Location Shared! Finding nearby hospitals...";
                
                // Format the data as JSON and store it in the hidden input
                document.getElementById("hospital_results").value = JSON.stringify({ latitude: lat, longitude: lon });
                
                // Trigger the custom event to notify Gradio that the value has changed
                document.getElementById("hospital_results").dispatchEvent(new Event('input'));
                
                // Show a temporary message to the user
                setTimeout(() => {
                    if (document.getElementById("status").innerText.includes("Finding")) {
                        document.getElementById("status").innerText = "✅ Location shared! Processing results...";
                    }
                }, 2000);
            },
            function(error) {
                let errorMsg = "";
                switch(error.code) {
                    case error.PERMISSION_DENIED:
                        errorMsg = "Location permission denied. Please allow location access to find nearby hospitals.";
                        break;
                    case error.POSITION_UNAVAILABLE:
                        errorMsg = "Location information unavailable. Please try again later.";
                        break;
                    case error.TIMEOUT:
                        errorMsg = "Location request timed out. Please try again.";
                        break;
                    default:
                        errorMsg = "Unknown error occurred.";
                }
                document.getElementById("status").innerText = "❌ " + errorMsg;
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }
        );
    } else {
        document.getElementById("status").innerText = "❌ Geolocation is not supported by your browser.";
    }
}

// Add a function to check for hospital-related queries and trigger location request
window.addEventListener('DOMContentLoaded', function() {
    // Use a more robust selector that works with Gradio's structure
    // Monitor all input elements and buttons in the chat interface
    const observer = new MutationObserver(function(mutations) {
        // Check if new messages were added to the chat
        const chatMessages = document.querySelectorAll('.message');
        if (chatMessages.length > 0) {
            // Get the last message (most recent)
            const lastMessage = chatMessages[chatMessages.length - 1];
            // If it's a bot message suggesting location access
            if (lastMessage.classList.contains('bot-message') && 
                (lastMessage.textContent.includes('allow location access') || 
                 lastMessage.innerHTML.includes('trigger-location-request'))) {
                // Trigger location request
                setTimeout(getLocation, 1000);
            }
        }
    });
    
    // Start observing the document with the configured parameters
    observer.observe(document.body, { childList: true, subtree: true });
    
    // Also monitor the input field and submit button
    document.body.addEventListener('click', function(e) {
        // Check if the clicked element is a submit button
        if (e.target.tagName === 'BUTTON' && 
            (e.target.textContent.includes('Submit') || 
             e.target.textContent.includes('Send') || 
             e.target.classList.contains('submit-btn'))) {
            // Find the nearest input field
            const inputs = document.querySelectorAll('input[type="text"], textarea');
            inputs.forEach(function(input) {
                checkForHospitalQuery(input.value);
            });
        }
    });
    
    // Monitor keypresses on the entire document
    document.body.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA')) {
            checkForHospitalQuery(e.target.value);
        }
    });
});

function checkForHospitalQuery(text) {
    if (!text) return;
    
    const hospitalKeywords = ['hospital', 'clinic', 'medical center', 'emergency', 'nearest', 'nearby'];
    const hasHospitalKeyword = hospitalKeywords.some(keyword => text.toLowerCase().includes(keyword));
    
    if (hasHospitalKeyword) {
        // Wait a short moment to allow the chatbot to process the message first
        setTimeout(() => {
            getLocation();
        }, 1000);
    }
}
</script>
"""

def process_input(text_input, audio_input, image_input, hospital_results=None):
    """Process user input (text, audio, or image) and get doctor's response"""
    # Initialize variables
    user_text = ""
    temp_audio_path = None
    doctor_response = ""
    doctor_audio_path = None
    
    try:
        # Get user location based on IP
        user_location = get_user_location()
        location_info = ""
        if user_location:
            location_info = f"\n\nPatient location: {user_location['city']}, {user_location['region']}, {user_location['country']} (Coordinates: {user_location['latitude']}, {user_location['longitude']})"
            print(f"User location detected: {location_info}")
        
        # Process text input
        if text_input:
            user_text = text_input
        
        # Process audio input
        if audio_input is not None:
            temp_audio_path = audio_input
            transcription = patient_voice.transcribe_audio(temp_audio_path)
            user_text = transcription
        
        # If no text input was provided or transcribed
        if not user_text.strip() and image_input is None:
            # Only return an error if there's no image and no text
            return "Please provide some text, speak clearly, or upload an image so I can understand your concern.", None, None
        
        # Check if hospital results are available from location sharing
        if hospital_results and hospital_results.strip():
            import json
            try:
                # Try to parse the hospital_results as JSON (from the location sharing button)
                location_data = json.loads(hospital_results)
                if 'latitude' in location_data and 'longitude' in location_data:
                    print(f"📍 Received precise user location: {location_data['latitude']}, {location_data['longitude']}")
                    
                    # Find nearby hospitals using the provided coordinates
                    hospitals = find_nearby_hospitals(
                        latitude=location_data['latitude'],
                        longitude=location_data['longitude'],
                        radius=5000,  # 5km radius
                        limit=5  # Top 5 results
                    )
                    
                    # Format the hospital results
                    formatted_results = format_hospital_results(hospitals)
                    
                    # Create a more user-friendly response
                    response = "📍 Based on your shared location, I found these nearby medical facilities:\n\n" + formatted_results
                    
                    return response, doctor_voice.text_to_speech(response), "Find nearby hospitals"
            except json.JSONDecodeError as e:
                print(f"Error parsing location data: {e}")
                # If it's not JSON, treat it as a pre-formatted string (for backward compatibility)
                return hospital_results, doctor_voice.text_to_speech(hospital_results), user_text
            except Exception as e:
                error_msg = f"Error processing location: {str(e)}"
                print(error_msg)
                return error_msg, doctor_voice.text_to_speech(error_msg), user_text
        
        # Check if user is asking about nearby hospitals or clinics
        hospital_keywords = ["hospital", "clinic", "medical center", "emergency room", "nearest hospital", "closest hospital"]
        location_keywords = ["near", "nearby", "closest", "nearest", "around", "find"]
        
        is_hospital_query = False
        for hospital_keyword in hospital_keywords:
            if hospital_keyword.lower() in user_text.lower():
                for location_keyword in location_keywords:
                    if location_keyword.lower() in user_text.lower():
                        is_hospital_query = True
                        break
                if is_hospital_query:
                    break
        
        # If user is asking about nearby hospitals
        if is_hospital_query:
            # Inform the user that we'll request their location and provide link to hosted site
            # Create a clean text version without HTML tags for display to the user
            hospital_response = (
                "I can help you find nearby hospitals and clinics. For the most accurate results, please visit:\n\n"
                "https://myhostt-1.onrender.com/\n\n"
                "This site will use your precise location to find the nearest medical facilities with accurate signals.\n\n"
                "Alternatively, I can try to find hospitals based on your browser location."
            )
            
            # We'll rely on JavaScript to detect hospital-related keywords instead of using hidden HTML triggers
            # This prevents raw HTML from being displayed to patients
            hospital_response_with_trigger = hospital_response  # No HTML tags added
            
            # The location request will be triggered by the JavaScript we added
            # which detects hospital-related queries and calls getLocation()
            
            # Use IP-based location data
            if user_location:
                # Find nearby hospitals using the user's IP-based location
                hospitals = find_nearby_hospitals(
                    latitude=user_location["latitude"],
                    longitude=user_location["longitude"],
                    radius=5000,  # 5km radius
                    limit=5  # Top 5 results
                )
                
                # Format the hospital results
                hospital_info = format_hospital_results(hospitals)
                
                # Add the hospital information to the response
                hospital_response += "\n\nBased on your approximate IP location, here are some nearby facilities:\n\n" + hospital_info
                # No longer adding HTML tags to the trigger version to prevent raw HTML display
                hospital_response_with_trigger = hospital_response  # Keep versions identical
            
            # Return the clean version without HTML tags for display to the user
            # The hidden trigger will be added via JavaScript detection of hospital-related keywords
            # This prevents raw HTML from being displayed to the patient
            return hospital_response, doctor_voice.text_to_speech(hospital_response), user_text
        else:
            # Add location information to user input if available
            if location_info and user_text:
                user_text = user_text + location_info
        
        # Get response from doctor brain
        if image_input is not None:
            # Pass the image directly to the doctor brain for processing with vision model
            doctor_response = doctor_brain.get_response(user_text, image_input)
        else:
            doctor_response = doctor_brain.get_response(user_text)
        
        # Convert doctor's response to speech
        doctor_audio_path = doctor_voice.text_to_speech(doctor_response)
        
        return doctor_response, doctor_audio_path, user_text
    
    except Exception as e:
        error_message = f"Error processing input: {str(e)}"
        print(error_message)
        return error_message, None, user_text



# Create Gradio interface
with gr.Blocks(css=custom_css) as app:
    
    
    # Add Generate Report button
    gr.HTML("<a href='https://reportsemail.onrender.com' target='_blank' class='generate-report-btn'>Generate Reports</a>")
    
    with gr.Row():
        with gr.Column(scale=3):
            gr.HTML("<h1 class='main-header'>AI Doctor with Vision and Voice</h1>")
            gr.HTML("<p class='sub-header'>Consult with our AI medical assistant using text, voice, or images</p>")
            gr.HTML("""
                <style>
                </style>
            """)
    
    with gr.Row():
        with gr.Column(scale=1):
            with gr.Group(elem_classes=["input-container"]):
                gr.HTML("<div class='input-label'>Patient Input</div>")
                text_input = gr.Textbox(placeholder="Describe your symptoms or ask a medical question...", label="Speech to Text")
                audio_input = gr.Audio(sources=["microphone"], label="Record your voice", elem_classes=["audio-player"])
                image_input = gr.Image(label="Upload an image (optional)", type="filepath", elem_classes=["image-upload"])
                
                # Location status display
                gr.HTML(location_js)
                gr.HTML("<p id='status' class='location-status'></p>")
                
                # Hidden input to store hospital results
                hospital_results = gr.Textbox(visible=False, elem_id="hospital_results")
                
                submit_btn = gr.Button("Get Medical Advice", elem_classes=["submit-btn"])
        
        with gr.Column(scale=1):
            with gr.Group(elem_classes=["output-container"]):
                gr.HTML("<div class='output-label'>Doctor's Response</div>")
                transcription_output = gr.Textbox(label="Your Input (Transcribed)", visible=True)
                response_output = gr.Textbox(label="Doctor's Response")
                audio_output = gr.Audio(label="Listen to Response", elem_classes=["audio-player"])
    


    # Set up event handlers
    submit_btn.click(
        fn=process_input,
        inputs=[text_input, audio_input, image_input, hospital_results],
        outputs=[response_output, audio_output, transcription_output]
    )
    
    # Also trigger when hospital_results changes (after location sharing)
    hospital_results.change(
        fn=process_input,
        inputs=[text_input, audio_input, image_input, hospital_results],
        outputs=[response_output, audio_output, transcription_output]
    )
    
    gr.HTML("<div class='footer'>This AI medical assistant is for informational purposes only. Always consult with a healthcare professional for medical advice.</div>")


# Launch the app
if __name__ == "__main__":
 app.launch(share=True)
    
