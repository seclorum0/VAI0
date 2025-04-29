import requests
from config import ELEVENLABS_API_KEY

url = "https://api.elevenlabs.io/v1/text-to-speech/EXAVITQu4vr4xnSDxMaL"
headers = {
    "xi-api-key": ELEVENLABS_API_KEY,
    "Content-Type": "application/json"
}
data = {
    "text": "Hello, I'm Elevenlabs here!",
    "model_id": "eleven_monolingual_v1",
    "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
}

response = requests.post(url, json=data, headers=headers)
print(f"Status Code: {response.status_code}")
print(f"Content-Type: {response.headers.get('Content-Type')}")

# Simpan file
output_file = "output.mp3"
with open(output_file, "wb") as f:
    f.write(response.content)

# Cek ukuran file
import os
file_size = os.path.getsize(output_file)
print(f"Ukuran file: {file_size} bytes")

# Coba putar (opsional)
import winsound
try:
    winsound.PlaySound(output_file, winsound.SND_FILENAME)
    print("File diputar!")
except Exception as e:
    print(f"Error saat memutar: {e}")