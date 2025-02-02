from flask import Flask, render_template, request, jsonify
import whisper
from gtts import gTTS
import os
from googletrans import Translator

app = Flask(__name__)

# Load Whisper model
model = whisper.load_model("base")

# Initialize Google Translate
translator = Translator()

# Temporary directory for audio files
AUDIO_DIR = "static/audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/translate", methods=["POST"])
def translate():
    # Get the uploaded audio file
    if "audio" not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    audio_file = request.files["audio"]
    audio_path = os.path.join(AUDIO_DIR, "input_audio.mp3")
    audio_file.save(audio_path)

    # Debug: Check if the file is saved correctly
    if not os.path.exists(audio_path):
        return jsonify({"error": "Failed to save audio file"}), 500

    # Get input and target languages
    input_language = request.form.get("input_language", "es")  # Default to Spanish
    target_language = request.form.get("target_language", "en")  # Default to English

    # Step 1: Convert speech to text using Whisper
    try:
        print(f"Transcribing audio in {input_language}...")
        result = model.transcribe(audio_path, language=input_language)
        original_text = result["text"]
        print("Transcription result:", original_text)
    except Exception as e:
        return jsonify({"error": f"Transcription failed: {str(e)}"}), 500

    # Step 2: Translate the text using Google Translate
    try:
        print(f"Translating text from {input_language} to {target_language}...")
        translated = translator.translate(original_text, src=input_language, dest=target_language)
        translated_text = translated.text
        print("Translated text:", translated_text)
    except Exception as e:
        return jsonify({"error": f"Translation failed: {str(e)}"}), 500

    # Step 3: Generate audio for the translated text using gTTS
    try:
        print("Generating audio...")
        tts = gTTS(translated_text, lang=target_language)
        audio_output_path = os.path.join(AUDIO_DIR, "translated_audio.mp3")
        tts.save(audio_output_path)
        print("Audio saved to:", audio_output_path)
    except Exception as e:
        return jsonify({"error": f"Audio generation failed: {str(e)}"}), 500

    # Return results
    return jsonify({
        "original_text": original_text,
        "translated_text": translated_text,
        "audio_url": f"/{audio_output_path}"
    })

if __name__ == "__main__":
    app.run(debug=True)