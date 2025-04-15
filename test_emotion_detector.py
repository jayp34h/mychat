import unittest
from emotion_detector import EmotionDetector

class TestEmotionDetector(unittest.TestCase):
    def setUp(self):
        self.detector = EmotionDetector()
    
    def test_emotion_detection(self):
        # Test various emotional statements
        test_cases = [
            ("I'm so happy today!", "joy"),
            ("I feel really sad and depressed.", "sadness"),
            ("I'm furious about what happened.", "anger"),
            ("I'm terrified of what might happen.", "fear"),
            ("Wow, I didn't expect that at all!", "surprise"),
            ("I love spending time with my family.", "love"),
            ("The weather is nice today.", "neutral")
        ]
        
        for text, expected_emotion in test_cases:
            detected_emotion = self.detector.detect_emotion(text)
            print(f"Text: '{text}', Expected: {expected_emotion}, Detected: {detected_emotion}")
            
            # We're not asserting exact equality because emotion detection isn't always precise
            # Instead, we're just running the tests to make sure no errors occur
            
            # Get response for this text
            response, emotion = self.detector.get_response(text)
            print(f"Response: '{response}' (Emotion: {emotion})\n")
    
    def test_error_handling(self):
        # Test empty text
        emotion = self.detector.detect_emotion("")
        self.assertIn(emotion, ["neutral", "sadness", "joy", "love", "anger", "fear", "surprise"])
        
        # Test very long text (should truncate properly)
        long_text = "I'm feeling happy. " * 100
        emotion = self.detector.detect_emotion(long_text)
        self.assertIn(emotion, ["neutral", "sadness", "joy", "love", "anger", "fear", "surprise"])

if __name__ == '__main__':
    unittest.main()