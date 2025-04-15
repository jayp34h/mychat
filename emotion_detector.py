import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from accelerate import init_empty_weights
import random

class EmotionDetector:
    def __init__(self):
        self.model_name = "bhadresh-savani/bert-base-uncased-emotion"
        self.tokenizer = None
        self.model = None
        
        # Define appropriate responses for each emotion with emojis
        self.emotion_responses = {
            "sadness": [
                "I understand this might be difficult. 😔 As your medical assistant, I'm here to help and support you.",
                "I hear the sadness in your words. 💙 Let's work together to address your concerns.",
                "It's natural to feel down when dealing with health issues. 🌧️ Would you like to tell me more?",
                "Your feelings are valid. 🤗 Let's focus on finding ways to help you feel better."
            ],
            "joy": [
                "I'm glad you're feeling positive! 😊 That's great for your overall well-being.",
                "Your optimism is wonderful! 🎉 It can really help with the healing process.",
                "That's excellent news! ☀️ A positive mindset can significantly impact your health.",
                "I'm happy to hear that! 😃 Let's maintain this positive energy in your healthcare journey."
            ],
            "love": [
                "It's wonderful to have a supportive network during your healthcare journey. ❤️",
                "Having caring relationships is crucial for well-being. 💖 I'm here to support you too.",
                "That kind of support is invaluable in healthcare. 💕 Let's build on that positive energy.",
                "It's heartwarming to hear about your support system. 🥰 They can be crucial in your recovery."
            ],
            "anger": [
                "I understand healthcare challenges can be frustrating. 😤 Let's address your concerns systematically.",
                "Your frustration is valid. 🔥 Would you like to explain what specific aspects are bothering you?",
                "Let's take a moment to breathe. 🧘 Then we can work on addressing what's upsetting you.",
                "I hear your frustration. 💪 Let's focus on finding constructive solutions together."
            ],
            "fear": [
                "It's normal to feel anxious about health matters. 😨 I'm here to help clarify any concerns.",
                "Many patients experience similar worries. 🌀 Let's discuss what's causing your anxiety.",
                "We can work through these concerns together. 🤝 What specific aspects are worrying you?",
                "Your health concerns are important. 🛡️ Let's address them one step at a time."
            ],
            "surprise": [
                "I understand this information might be unexpected. 😲 Let me help you process it.",
                "Sometimes medical information can be surprising. 🎭 Would you like me to explain further?",
                "I can help you understand these unexpected findings. 😮 What questions do you have?",
                "Let's work through this new information together. 🌟 I'm here to clarify any concerns."
            ],
            "neutral": [
                "How can I assist you with your health concerns today? 🌈",
                "I'm here to help with any medical questions you might have. 🙂",
                "Let's discuss your health needs and concerns. 🌱",
                "I'm ready to assist you with your healthcare journey. 📝"
            ]
        }
        
        # Load the model
        self.load_model()
    
    def load_model(self):
        """Load the pre-trained emotion detection model and tokenizer"""
        try:
            print("Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            print("Loading model...")
            # Remove init_empty_weights() and load model directly
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            # Move model to CPU or GPU if available
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model = self.model.to(device)
            self.model.eval()  # Set model to evaluation mode
            print(f"Model loaded successfully on {device}! 🚀")
        except Exception as e:
            print(f"Error loading model: {str(e)} ❌")
    
    def detect_emotion(self, text):
        """Detect emotion from input text"""
        if not text:
            return "neutral"
        
        # Truncate text if it's too long
        max_length = 512
        if len(text.split()) > max_length:
            text = " ".join(text.split()[:max_length])
        
        try:
            # Tokenize and prepare input
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            device = next(self.model.parameters()).device
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            # Get model prediction
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = outputs.logits.softmax(dim=-1)
                emotion_idx = predictions.argmax().item()
            
            # Map prediction to emotion label
            emotions = ["sadness", "joy", "love", "anger", "fear", "surprise", "neutral"]
            return emotions[emotion_idx]
        except Exception as e:
            print(f"Error detecting emotion: {str(e)} ❌")
            return "neutral"
    
    def get_response(self, text):
        """Generate appropriate response based on detected emotion"""
        emotion = self.detect_emotion(text)
        responses = self.emotion_responses.get(emotion, self.emotion_responses["neutral"])
        return random.choice(responses), emotion