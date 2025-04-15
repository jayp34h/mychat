import sys
import os

# Add the parent directory to the path so we can import the module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from voice_of_patient import PatientVoice

# Create an instance of PatientVoice
patient_voice = PatientVoice()

# Print success message
print('PatientVoice module loaded successfully')