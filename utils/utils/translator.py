from googletrans import Translator
from gtts import gTTS
import os

translator = Translator()

def translate_text(text, target_lang):
    try:
        translated = translator.translate(text, dest=target_lang)
        return translated.text
    except Exception as e:
        raise Exception(f"Translation failed: {str(e)}")

def text_to_speech(text, lang, output_path):
    try:
        tts = gTTS(text=text, lang=lang)
        tts.save(output_path)
    except Exception as e:
        raise Exception(f"Text-to-speech failed: {str(e)}")
