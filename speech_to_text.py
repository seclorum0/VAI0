import speech_recognition as sr

def get_audio():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Bilang sesuatu...")
        audio = recognizer.listen(source, timeout=5)
        try:
            text = recognizer.recognize_google(audio, language="id-ID")
            print(f"Kamu bilang: {text}")
            return text
        except sr.UnknownValueError:
            print("Maaf, tidak bisa mengerti.")
            return None
        except sr.RequestError:
            print("Error dengan layanan Google Speech.")
            return None

if __name__ == "__main__":
    text = get_audio()