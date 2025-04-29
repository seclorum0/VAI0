import sys
import os
import numpy as np
import threading
import time
import speech_recognition as sr
import ollama
import requests
from pygame import mixer
from io import BytesIO
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, 
                            QVBoxLayout, QHBoxLayout)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QSize, QTimer
from PyQt5.QtGui import QPainter, QColor, QRadialGradient, QPen, QBrush, QPainterPath
from config import ELEVENLABS_API_KEY

class AudioThread(QThread):
    """Thread for handling audio recording and processing"""
    audio_level = pyqtSignal(int)  # Signal to emit audio levels (0-100)
    transcription = pyqtSignal(str)  # Signal to emit transcribed text
    error = pyqtSignal(str)  # Signal to emit errors
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.recognizer = sr.Recognizer()
        
    def run(self):
        self.running = True
        while self.running:
            try:
                with sr.Microphone() as source:
                    # Adjust for ambient noise
                    self.recognizer.adjust_for_ambient_noise(source)
                    print("Say something...")
                    
                    # Listen for audio
                    audio = self.recognizer.listen(source, timeout=5)
                    
                    # Get audio data for visualization
                    # This is a simplified approach - in a real implementation,
                    # you would analyze the audio data in real-time
                    audio_data = audio.get_raw_data()
                    frames = len(audio_data) // 2
                    
                    # Process audio data in chunks to simulate real-time visualization
                    chunk_size = frames // 20
                    for i in range(0, frames, chunk_size):
                        if not self.running:
                            break
                        
                        # Calculate audio level from chunk
                        chunk = audio_data[i*2:(i+chunk_size)*2]
                        if chunk:
                            # Simple amplitude calculation
                            amplitude = np.frombuffer(chunk, dtype=np.int16)
                            level = min(100, int(np.abs(amplitude).mean() / 100))
                            self.audio_level.emit(level)
                        
                        time.sleep(0.05)  # Simulate real-time processing
                    
                    # Try to recognize speech
                    text = self.recognizer.recognize_google(audio, language="en-US")
                    if text and self.running:
                        print(f"Chat: {text}")
                        self.transcription.emit(text)
                        
            except sr.WaitTimeoutError:
                # No speech detected, continue listening
                pass
            except sr.UnknownValueError:
                print("Sorry, I couldn't understand.")
                self.error.emit("Could not understand audio")
            except sr.RequestError as e:
                print(f"Error with Google Speech service: {e}")
                self.error.emit(f"Error with speech recognition service: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")
                self.error.emit(f"Unexpected error: {e}")
                
    def stop(self):
        self.running = False
        self.wait()


class LLMThread(QThread):
    """Thread for handling LLM processing"""
    response = pyqtSignal(str)  # Signal to emit LLM response
    error = pyqtSignal(str)  # Signal to emit errors
    
    def __init__(self):
        super().__init__()
        self.prompt = None
        
    def set_prompt(self, prompt):
        self.prompt = prompt
        
    def run(self):
        if not self.prompt:
            return
            
        try:
            print(f"Processing with LLM: {self.prompt}")
            # Get response from Ollama
            response = ollama.chat(model='llama2', messages=[
                {'role': 'system', 'content': 'Respond in English only.'},
                {'role': 'user', 'content': self.prompt}
            ])
            
            response_text = response['message']['content']
            print(f"VAI0: {response_text}")
            
            # Emit the response
            self.response.emit(response_text)
            
        except Exception as e:
            print(f"Error with LLM: {e}")
            self.error.emit(f"Error with LLM: {e}")


class TTSThread(QThread):
    """Thread for handling text-to-speech conversion and playback"""
    playback_started = pyqtSignal()  # Signal when audio playback starts
    playback_finished = pyqtSignal()  # Signal when audio playback finishes
    error = pyqtSignal(str)  # Signal to emit errors
    
    def __init__(self):
        super().__init__()
        self.text = None
        
    def set_text(self, text):
        self.text = text
        
    def run(self):
        if not self.text:
            return
            
        try:
            print(f"Converting to speech: {self.text}")
            url = "https://api.elevenlabs.io/v1/text-to-speech/EXAVITQu4vr4xnSDxMaL"
            headers = {
                "xi-api-key": ELEVENLABS_API_KEY,
                "Content-Type": "application/json"
            }
            data = {
                "text": self.text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
            }
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                print("Speech generated successfully, playing audio...")
                # Initialize mixer
                mixer.init()
                
                # Load audio from memory
                audio_data = BytesIO(response.content)
                mixer.music.load(audio_data)
                
                # Signal that playback is starting
                self.playback_started.emit()
                
                # Play audio
                mixer.music.play()
                
                # Wait for playback to finish
                while mixer.music.get_busy():
                    time.sleep(0.1)
                    
                # Signal that playback is finished
                self.playback_finished.emit()
                print("Audio playback completed")
                
            else:
                error_msg = f"Error from ElevenLabs: Status {response.status_code}"
                print(error_msg)
                self.error.emit(error_msg)
                
        except Exception as e:
            print(f"Error with TTS: {e}")
            self.error.emit(f"Error with TTS: {e}")


class VoiceVisualizer(QWidget):
    """Widget for visualizing voice input with a dynamic, responsive animation"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(300, 300)
        self._radius = 50  # Default radius
        self._max_radius = 250
        self._intensity = 0  # Voice intensity (0-100)
        self._visible = False
        self._wave_offset = 0  # For wave animation effect
        
        # Timer for animation
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(50)  # 20 fps
        
    def update_animation(self):
        """Update animation parameters"""
        if self._visible:
            # Update wave offset for flowing effect
            self._wave_offset = (self._wave_offset + 5) % 360
            self.update()
        
    def set_intensity(self, intensity):
        """Set the voice intensity level (0-100)"""
        self._intensity = max(0, min(100, intensity))
        # Calculate radius based on intensity with some smoothing
        target_radius = 50 + (self._max_radius - 50) * (self._intensity / 100)
        # Smooth transition
        self._radius = self._radius * 0.7 + target_radius * 0.3
        self.update()  # Trigger repaint
        
    def set_visible(self, visible):
        """Show or hide the visualizer"""
        self._visible = visible
        if not visible:
            self._intensity = 0
            self._radius = 50
        self.update()
        
    def paintEvent(self, event):
        if not self._visible:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Center of the widget
        center_x = self.width() // 2
        center_y = self.height() // 2
        
        # Base radius with wave effect
        base_radius = self._radius
        
        # Create radial gradient (black to deep purple)
        gradient = QRadialGradient(center_x, center_y, base_radius)
        gradient.setColorAt(0, QColor(0, 0, 0))  # Black at center
        gradient.setColorAt(1, QColor(48, 25, 52))  # Deep purple at edge
        
        # Draw the main circle
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(gradient))
        
        # Calculate wave effect
        num_waves = 8
        wave_amplitude = 5 + (self._intensity / 20)  # Intensity affects wave size
        
        # Draw circle with wavy edges
        path = QPainterPath()
        for angle in range(0, 360, 1):
            rad_angle = np.radians(angle)
            # Wave effect based on sine function
            wave = wave_amplitude * np.sin(num_waves * rad_angle + np.radians(self._wave_offset))
            radius = base_radius + wave
            
            x = center_x + radius * np.cos(rad_angle)
            y = center_y + radius * np.sin(rad_angle)
            
            if angle == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
                
        path.closeSubpath()
        painter.drawPath(path)


class VAI0App(QMainWindow):
    """Main application window for the VAI0 speech-to-speech AI system"""
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initThreads()
        
    def initUI(self):
        # Set window properties
        self.setWindowTitle('VAI0')
        self.setMinimumSize(800, 600)
        self.setStyleSheet("background-color: white;")
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(50, 50, 50, 50)
        
        # Create voice visualizer
        self.visualizer = VoiceVisualizer()
        self.main_layout.addWidget(self.visualizer, alignment=Qt.AlignCenter)
        
        # Create button layout
        self.button_layout = QHBoxLayout()
        self.main_layout.addLayout(self.button_layout)
        
        # Create start button
        self.start_button = QPushButton("Start")
        self.start_button.setFixedSize(120, 120)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #000000;
                color: white;
                border: 1px solid #333333;
                border-radius: 60px;
                font-family: Arial;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #1A1A1A;
            }
        """)
        self.button_layout.addWidget(self.start_button, alignment=Qt.AlignCenter)
        
        # Create stop button (initially hidden)
        self.stop_button = QPushButton("Stop")
        self.stop_button.setFixedSize(80, 80)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #8B0000;
                color: white;
                border: 1px solid #333333;
                border-radius: 40px;
                font-family: Arial;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #A52A2A;
            }
        """)
        self.stop_button.hide()  # Initially hidden
        self.button_layout.addWidget(self.stop_button, alignment=Qt.AlignRight)
        
        # Connect button signals
        self.start_button.clicked.connect(self.start_recording)
        self.stop_button.clicked.connect(self.stop_recording)
        
        # Center the start button initially
        self.button_layout.setAlignment(Qt.AlignCenter)
        
    def initThreads(self):
        """Initialize worker threads"""
        # Audio processing thread
        self.audio_thread = AudioThread()
        self.audio_thread.audio_level.connect(self.update_visualization)
        self.audio_thread.transcription.connect(self.process_transcription)
        self.audio_thread.error.connect(self.handle_error)
        
        # LLM processing thread
        self.llm_thread = LLMThread()
        self.llm_thread.response.connect(self.process_llm_response)
        self.llm_thread.error.connect(self.handle_error)
        
        # TTS processing thread
        self.tts_thread = TTSThread()
        self.tts_thread.playback_started.connect(self.on_playback_started)
        self.tts_thread.playback_finished.connect(self.on_playback_finished)
        self.tts_thread.error.connect(self.handle_error)
        
    def start_recording(self):
        """Start the recording and processing loop"""
        # Show the visualizer
        self.visualizer.set_visible(True)
        
        # Move start button to bottom left
        self.button_layout.setAlignment(Qt.AlignLeft)
        
        # Show stop button
        self.stop_button.show()
        
        # Start the audio thread
        self.audio_thread.start()
        
    def stop_recording(self):
        """Stop the recording and processing loop"""
        # Stop the audio thread
        self.audio_thread.stop()
        
        # Hide the visualizer
        self.visualizer.set_visible(False)
        
        # Move start button back to center
        self.button_layout.setAlignment(Qt.AlignCenter)
        
        # Hide stop button
        self.stop_button.hide()
        
    def update_visualization(self, level):
        """Update the visualization based on audio level"""
        self.visualizer.set_intensity(level)
        
    def process_transcription(self, text):
        """Process transcribed text by sending to LLM"""
        # Send to LLM for processing
        self.llm_thread.set_prompt(text)
        self.llm_thread.start()
        
    def process_llm_response(self, response):
        """Process LLM response by sending to TTS"""
        # Send to TTS for conversion
        self.tts_thread.set_text(response)
        self.tts_thread.start()
        
    def on_playback_started(self):
        """Handle TTS playback start"""
        # Set visualizer to passive state during playback
        self.visualizer.set_intensity(30)
        
    def on_playback_finished(self):
        """Handle TTS playback finish"""
        # Resume listening if still active
        if self.audio_thread.running:
            pass  # Continue with normal operation
            
    def handle_error(self, error_msg):
        """Handle errors from threads"""
        print(f"Error: {error_msg}")
        
    def closeEvent(self, event):
        """Handle window close event"""
        # Stop all threads
        self.audio_thread.stop()
        if self.llm_thread.isRunning():
            self.llm_thread.terminate()
        if self.tts_thread.isRunning():
            self.tts_thread.terminate()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VAI0App()
    window.show()
    sys.exit(app.exec_())
