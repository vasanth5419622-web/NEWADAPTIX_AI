import base64
import urllib.parse
from typing import Dict, Any, Optional

class VoiceService:
    """
    Agricultural Voice Engine:
    - Speech-to-Text (STT) for natural farmer queries in English & Tamil.
    - Text-to-Speech (TTS) for spoken advisory delivery.
    """
    def transcribe(self, audio_base64: Optional[str] = None, text_fallback: Optional[str] = None, language: str = "en") -> Dict[str, Any]:
        # If client provided text from Web Speech API recognition, use it
        if text_fallback:
            return {
                "transcript": text_fallback,
                "language": language,
                "confidence": 0.95,
                "source": "client_speech_recognition"
            }
            
        # Example backend audio decoding simulation / placeholder
        if audio_base64:
            return {
                "transcript": "My crop leaves have yellow spots and necrotic borders.",
                "language": language,
                "confidence": 0.90,
                "source": "backend_stt_engine"
            }

        return {
            "transcript": "",
            "language": language,
            "confidence": 0.0,
            "source": "none"
        }

    def synthesize_advisory(
        self,
        crop: str,
        condition: str,
        confidence_level: str,
        management_advice: list,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Generates localized spoken advisory scripts in English and Tamil.
        """
        if language == "ta":
            # Translate crop names to Tamil
            tamil_crops = {
                "tomato": "தக்காளி",
                "chilli": "மிளகாய்",
                "rice": "நெல்",
                "potato": "உருளைக்கிழங்கு",
                "cotton": "பருத்தி"
            }
            crop_ta = tamil_crops.get(crop.lower(), crop)
            
            # Formulate clear, natural Tamil speech
            advice_summary_ta = "பாதிக்கப்பட்ட இலைகளை உடனே அப்புறப்படுத்தவும். தேவையான பாதுகாப்பு மருந்துகளை வேளாண்மை அதிகாரியின் வழிகாட்டுதலோடு பயன்படுத்தவும்."
            if "blight" in condition.lower():
                condition_ta = "ஆரம்பகால இலைக்கருகல் பூஞ்சை நோய்"
                advice_summary_ta = "கீழ் இலைகளில் உள்ள கருகிய பகுதிகளை நீக்கவும். மேல் தெளிப்பு நீர்ப்பாசனத்தை தவிர்த்து சொட்டு நீர்ப்பாசனம் பயன்படுத்தவும். மேங்கோசெப் அல்லது காப்பர் ஆக்ஸிகுளோரைடு பரிந்துரைக்கப்படுகிறது."
            elif "curl" in condition.lower():
                condition_ta = "இலைச்சுருட்டல் வைரஸ் மற்றும் தண்டு துளைப்பான் பூச்சி தாக்குதல்"
                advice_summary_ta = "வெள்ளை ஈக்களை கட்டுப்படுத்த ஏக்கருக்கு 15 முதல் 20 மஞ்சள் ஒட்டும் பொறிகளை வைக்கவும். வேப்பெண்ணெய் கரைசல் 3 மில்லி ஒரு லிட்டர் தண்ணீரில் கலந்து தெளிக்கவும்."
            elif "blast" in condition.lower():
                condition_ta = "நெல் குலை நோய்"
                advice_summary_ta = "அதிகப்படியான தழைச்சத்து உரங்களை தவிர்க்கவும். ட்ரைசைக்ளசோல் மருந்தை பரிந்துரைக்கப்பட்ட அளவில் தெளிக்கவும்."
            else:
                condition_ta = condition
                
            conf_ta = "உயர் நிலை" if confidence_level.lower() == "high" else "நடுத்தர நிலை"

            speech_script = (
                f"வணக்கம் விவசாயி அவர்களே. உங்கள் {crop_ta} பயிர் பரிசோதனை அறிக்கை: "
                f"கண்டறியப்பட்ட பாதிப்பு: {condition_ta}. "
                f"கணினி நம்பகத்தன்மை: {conf_ta}. "
                f"முக்கிய நடவடிக்கை: {advice_summary_ta} "
                f"மேலும் விவரங்களுக்கு அருகிலுள்ள வேளாண் விரிவாக்க அலுவலரை அணுகவும்."
            )
        else:
            first_advice = management_advice[0] if management_advice else "Inspect affected foliage and follow IPM guidelines."
            speech_script = (
                f"Hello farmer. Assessment for your {crop} crop is complete. "
                f"Possible condition detected is: {condition}. "
                f"System confidence is {confidence_level}. "
                f"Recommended immediate action: {first_advice} "
                f"Please consult your local agricultural extension officer before applying chemical treatments."
            )

        return {
            "text": speech_script,
            "language": language,
            "lang_code": "ta-IN" if language == "ta" else "en-US",
            "rate": 0.92 if language == "ta" else 0.98,
            "pitch": 1.0,
            "status": "ready"
        }

    def synthesize(self, text: str, language: str = "en") -> Dict[str, Any]:
        """
        Generic text-to-speech fallback.
        """
        return {
            "text": text,
            "language": language,
            "lang_code": "ta-IN" if language == "ta" else "en-US",
            "rate": 0.95,
            "pitch": 1.0,
            "status": "ready"
        }

voice_service = VoiceService()

