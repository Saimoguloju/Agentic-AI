import openai
import os
import tempfile
import pygame
import pyaudio
import wave
import threading
import time
from pathlib import Path
from dotenv import load_dotenv
import keyboard
import io

# Load environment variables
load_dotenv()

class VoiceConversationSystem:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.is_recording = False
        self.is_playing = False
        self.conversation_history = []
        
        # Audio settings
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        
        # Initialize pygame for audio playback
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Available voices
        self.voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        self.current_voice = "alloy"
        
        # Available models
        self.models = ["gpt-4o", "gpt-4", "gpt-3.5-turbo", "gpt-4o-mini"]
        self.current_model = "gpt-4o"
        
    def record_audio(self, filename, duration=None):
        """Record audio from microphone"""
        try:
            audio = pyaudio.PyAudio()
            
            stream = audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK
            )
            
            print("🎤 Recording... (Press 'q' to stop)")
            frames = []
            
            start_time = time.time()
            if duration:
                # Record for specific duration
                for _ in range(0, int(self.RATE / self.CHUNK * duration)):
                    data = stream.read(self.CHUNK)
                    frames.append(data)
            else:
                # Record until user stops or timeout
                while self.is_recording and (time.time() - start_time) < 30:  # 30 sec max
                    try:
                        data = stream.read(self.CHUNK, exception_on_overflow=False)
                        frames.append(data)
                        
                        # Check for keyboard interrupt
                        if keyboard.is_pressed('q'):
                            break
                    except Exception as e:
                        print(f"Recording error: {e}")
                        break
            
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
            # Save audio file
            wf = wave.open(filename, 'wb')
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(audio.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            print("✅ Recording stopped")
            return True
            
        except Exception as e:
            print(f"❌ Recording error: {e}")
            return False
        
    def speech_to_text(self, audio_file):
        """Convert speech to text using Whisper"""
        try:
            with open(audio_file, "rb") as file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=file,
                    response_format="text"
                )
            return transcript.strip()
        except Exception as e:
            print(f"❌ Speech-to-text error: {e}")
            return None
    
    def text_to_speech(self, text):
        """Convert text to speech using OpenAI TTS and return audio data"""
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=self.current_voice,
                input=text,
                speed=1.0
            )
            
            # Return the audio content as bytes
            return response.content
            
        except Exception as e:
            print(f"❌ Text-to-speech error: {e}")
            return None
    
    def play_audio_from_bytes(self, audio_bytes):
        """Play audio from bytes using pygame"""
        try:
            # Create a temporary file that we can manage better
            temp_dir = tempfile.gettempdir()
            temp_filename = f"tts_audio_{int(time.time())}.mp3"
            temp_path = os.path.join(temp_dir, temp_filename)
            
            # Write audio bytes to file
            with open(temp_path, 'wb') as f:
                f.write(audio_bytes)
            
            # Play the audio
            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
            
            # Clean up the file after playback
            time.sleep(0.5)  # Give it a moment
            try:
                os.remove(temp_path)
            except:
                pass  # File might still be in use, that's okay
                
            return True
            
        except Exception as e:
            print(f"❌ Audio playback error: {e}")
            return False
    
    def play_audio_file(self, filename):
        """Play audio file using pygame"""
        try:
            if not os.path.exists(filename):
                print(f"❌ Audio file not found: {filename}")
                return False
                
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
                
            return True
            
        except Exception as e:
            print(f"❌ Audio playback error: {e}")
            return False
    
    def get_ai_response(self, user_input):
        """Get response from OpenAI chat model"""
        try:
            # Add user message to conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            
            # Get AI response
            response = self.client.chat.completions.create(
                model=self.current_model,
                messages=self.conversation_history,
                max_tokens=150,  # Keep responses concise for voice
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            # Add AI response to conversation history
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            return ai_response
            
        except Exception as e:
            print(f"❌ AI response error: {e}")
            return "Sorry, I encountered an error. Could you please try again?"
    
    def voice_conversation_loop(self):
        """Main conversation loop"""
        print("🎙️ Voice Conversation System Started!")
        print(f"🤖 Current Model: {self.current_model}")
        print(f"🔊 Current Voice: {self.current_voice}")
        print("\nCommands:")
        print("- 'v' for voice input (record and speak)")
        print("- 't' for text input")
        print("- 'voice:name' to change voice (alloy, echo, fable, onyx, nova, shimmer)")
        print("- 'model:name' to change model (gpt-4o, gpt-4, gpt-3.5-turbo, gpt-4o-mini)")
        print("- 'clear' to clear conversation history")
        print("- 'q' or 'quit' to exit")
        print("-" * 50)
        
        while True:
            try:
                # Get user input method choice
                input_method = input("\n📝 Choose input method (v=voice, t=text, q=quit): ").strip().lower()
                
                if input_method in ['q', 'quit']:
                    break
                elif input_method == 'clear':
                    self.conversation_history = []
                    print("🗑️ Conversation history cleared")
                    continue
                elif input_method.startswith('voice:'):
                    voice_name = input_method.split(':')[1].strip()
                    if voice_name in self.voices:
                        self.current_voice = voice_name
                        print(f"🔊 Voice changed to: {voice_name}")
                    else:
                        print(f"❌ Invalid voice. Available: {', '.join(self.voices)}")
                    continue
                elif input_method.startswith('model:'):
                    model_name = input_method.split(':')[1].strip()
                    if model_name in self.models:
                        self.current_model = model_name
                        print(f"🤖 Model changed to: {model_name}")
                    else:
                        print(f"❌ Invalid model. Available: {', '.join(self.models)}")
                    continue
                
                user_input = None
                
                if input_method == 'v':
                    # Voice input
                    print("🎤 Get ready to speak...")
                    input("Press Enter when ready to start recording...")
                    
                    # Create temporary audio file
                    temp_dir = tempfile.gettempdir()
                    audio_filename = f"voice_input_{int(time.time())}.wav"
                    audio_path = os.path.join(temp_dir, audio_filename)
                    
                    self.is_recording = True
                    
                    # Record in a separate thread
                    record_thread = threading.Thread(
                        target=self.record_audio, 
                        args=(audio_path,)
                    )
                    record_thread.start()
                    
                    # Wait for recording to finish
                    record_thread.join()
                    self.is_recording = False
                    
                    # Convert speech to text
                    if os.path.exists(audio_path):
                        print("🔄 Converting speech to text...")
                        user_input = self.speech_to_text(audio_path)
                        
                        # Clean up audio file
                        try:
                            os.remove(audio_path)
                        except:
                            pass
                    else:
                        print("❌ Recording failed")
                        continue
                
                elif input_method == 't':
                    # Text input
                    user_input = input("💬 You: ").strip()
                
                if not user_input:
                    print("❌ No input received. Please try again.")
                    continue
                
                print(f"📝 You said: {user_input}")
                
                # Get AI response
                print("🤔 AI is thinking...")
                ai_response = self.get_ai_response(user_input)
                print(f"🤖 AI: {ai_response}")
                
                # Convert AI response to speech and play
                print("🔄 Converting AI response to speech...")
                audio_bytes = self.text_to_speech(ai_response)
                
                if audio_bytes:
                    print("🔊 Playing AI response...")
                    self.play_audio_from_bytes(audio_bytes)
                else:
                    print("❌ Failed to generate speech")
                
            except KeyboardInterrupt:
                print("\n👋 Conversation interrupted by user")
                break
            except Exception as e:
                print(f"❌ Error in conversation loop: {e}")
    
    def test_system(self):
        """Test all system components"""
        print("🧪 Testing Voice Conversation System...")
        
        # Test TTS
        print("1️⃣ Testing Text-to-Speech...")
        test_text = "Hello! This is a test of the text to speech system."
        
        audio_bytes = self.text_to_speech(test_text)
        if audio_bytes:
            print("✅ TTS working - generating audio...")
            if self.play_audio_from_bytes(audio_bytes):
                print("✅ Audio playback working")
            else:
                print("❌ Audio playback failed")
        else:
            print("❌ TTS failed")
        
        # Test AI response
        print("2️⃣ Testing AI Response...")
        response = self.get_ai_response("Hello, can you hear me?")
        print(f"✅ AI Response: {response}")
        
        print("3️⃣ Voice recording test requires user interaction during conversation")
        print("✅ System test completed!")

def check_requirements():
    """Check if all required packages are installed"""
    required_packages = {
        'openai': 'openai',
        'dotenv': 'python-dotenv',
        'pygame': 'pygame',
        'pyaudio': 'pyaudio',
        'keyboard': 'keyboard'
    }
    
    missing_packages = []
    
    for package, pip_name in required_packages.items():
        try:
            __import__(package)
            print(f"✅ {pip_name} is installed")
        except ImportError:
            print(f"❌ {pip_name} is missing")
            missing_packages.append(pip_name)
    
    if missing_packages:
        print(f"\n📦 Install missing packages with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

if __name__ == "__main__":
    print("🎙️ Voice Conversation System with OpenAI")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        print("❌ Please install missing packages first")
        exit(1)
    
    # Check API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("Please set your API key in .env file or environment variables")
        exit(1)
    
    # Initialize system
    try:
        voice_system = VoiceConversationSystem()
        print("✅ Voice system initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize voice system: {e}")
        exit(1)
    
    # Test system
    choice = input("\n🧪 Run system test first? (y/n): ").strip().lower()
    if choice == 'y':
        voice_system.test_system()
    
    # Start conversation
    choice = input("\n🚀 Start voice conversation? (y/n): ").strip().lower()
    if choice == 'y':
        voice_system.voice_conversation_loop()
    
    print("👋 Goodbye!")