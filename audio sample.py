from gtts import gTTS

# Text to convert to speech
text = "Hola"

# Generate audio
tts = gTTS(text, lang="es")
tts.save("es2_audio.mp3")

print("Audio file saved as es2_audio.mp3")