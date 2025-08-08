import logging
import wave
import vosk
import os
import json
import librosa
import soundfile as sf
from pathlib import Path

logger = logging.getLogger(__name__)

class VoskTranscriber:
    def __init__(self, model_path: str = None):
        """Initialize Vosk transcriber with model"""
        try:
            if model_path is None:
                model_path = os.path.join(os.path.dirname(__file__), "..", "models", "vosk-model-en-us-0.22")
            
            self.model_path = Path(model_path)
            self._download_model_if_needed()
            
            logger.info(f"Loading Vosk model from {self.model_path}")
            self.model = vosk.Model(str(self.model_path))
            # Initialize recognizer with 16kHz sample rate (Vosk requirement)
            self.recognizer = vosk.KaldiRecognizer(self.model, 16000)
            self.model_loaded = True
            logger.info("Vosk model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load Vosk model: {str(e)}")
            self.model_loaded = False
            self.model = None
            self.recognizer = None
        
    def _download_model_if_needed(self):
        """Download Vosk model if not present"""
        if not self.model_path.exists():
            logger.info("Vosk model not found, downloading...")
            os.makedirs(self.model_path.parent, exist_ok=True)
            
            # Download and extract model
            import urllib.request
            import zipfile
            
            model_url = "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip"
            zip_path = self.model_path.parent / "model.zip"
            
            logger.info("Downloading Vosk model (this may take a few minutes)...")
            urllib.request.urlretrieve(model_url, zip_path)
            
            logger.info("Extracting model...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.model_path.parent)
            
            # Remove zip file
            os.remove(zip_path)
            logger.info("Model download completed")

    def transcribe(self, audio_path: str) -> str:
        """Transcribe audio file to text - REAL TRANSCRIPTION ONLY"""
        print(f"🔄 Starting REAL transcription for: {audio_path}")
        
        # Check if model is loaded
        if not self.model_loaded:
            print("❌ Vosk model not loaded")
            return "Error: Speech recognition model not available. Please restart the server."
        
        # First, try to get file info
        try:
            import os
            file_size = os.path.getsize(audio_path)
            print(f"📁 Input file size: {file_size} bytes")
            
            if file_size < 100:
                raise Exception("Audio file too small or corrupted")
                
        except Exception as e:
            print(f"❌ File check failed: {str(e)}")
            return f"Error: Could not read audio file - {str(e)}"
        
        # Try real transcription methods
        transcription_methods = [
            self._transcribe_real_audio,
            self._transcribe_fallback
        ]
        
        for i, method in enumerate(transcription_methods):
            try:
                print(f"🔧 Trying transcription method {i+1}")
                result = method(audio_path)
                if result and result.strip() and not result.startswith("Error:"):
                    print(f"✅ Transcription successful with method {i+1}")
                    return result
            except Exception as e:
                print(f"❌ Transcription method {i+1} failed: {str(e)}")
                continue
        
        return "Transcription failed. Please try a different audio file or speak more clearly."
    
    def _transcribe_real_audio(self, audio_path: str) -> str:
        """Real transcription using Vosk with enhanced debugging"""
        print(f"🎯 Starting REAL transcription with Vosk for: {audio_path}")
        print(f"📊 Model loaded status: {self.model_loaded}")
        
        try:
            # Step 1: Convert audio to proper format
            print("🔄 Step 1: Converting audio to WAV format...")
            wav_path = self._convert_to_wav(audio_path)
            print(f"✅ Audio converted to: {wav_path}")
            
            # Step 2: Get audio info
            print("🔄 Step 2: Getting audio information...")
            import soundfile as sf
            audio_info = sf.info(wav_path)
            print(f"📊 Audio info - Channels: {audio_info.channels}, Sample Rate: {audio_info.samplerate}, Duration: {audio_info.duration:.2f}s")
            
            # Step 3: Process with Vosk
            print("🔄 Step 3: Processing with Vosk...")
            result = self._process_wav_file(wav_path)
            print(f"🎤 Vosk result: '{result}'")
            
            # Step 4: Clean up
            print("🔄 Step 4: Cleaning up temporary files...")
            if os.path.exists(wav_path) and wav_path != audio_path:
                os.unlink(wav_path)
                print(f"🗑️ Cleaned up: {wav_path}")
            
            if result and result.strip():
                print(f"✅ Transcription successful: '{result[:100]}...'")
                return result
            else:
                print("❌ Vosk returned empty result")
                raise Exception("Vosk returned empty transcription")
                
        except Exception as e:
            print(f"❌ Real transcription failed: {str(e)}")
            print(f"🔍 Error type: {type(e).__name__}")
            import traceback
            print(f"📋 Full traceback: {traceback.format_exc()}")
            raise
    
    def _process_wav_file(self, wav_path: str) -> str:
        """Process WAV file with Vosk and detailed debugging"""
        print(f"🎤 Processing WAV file with Vosk: {wav_path}")
        
        try:
            import wave
            with wave.open(wav_path, 'rb') as wf:
                print(f"📊 WAV file details:")
                print(f"   - Channels: {wf.getnchannels()}")
                print(f"   - Sample rate: {wf.getframerate()} Hz")
                print(f"   - Sample width: {wf.getsampwidth()} bytes")
                print(f"   - Frames: {wf.getnframes()}")
                print(f"   - Duration: {wf.getnframes() / wf.getframerate():.2f} seconds")
                
                # Verify format
                if wf.getnchannels() != 1:
                    print("⚠️ Warning: Audio is not mono")
                if wf.getframerate() != 16000:
                    print("⚠️ Warning: Sample rate is not 16kHz")
                if wf.getsampwidth() != 2:
                    print("⚠️ Warning: Sample width is not 16-bit")
            
            # Process with Vosk following official documentation
            print("🔄 Starting Vosk recognition...")
            
            # Read audio data
            with wave.open(wav_path, 'rb') as wf:
                audio_data = wf.readframes(wf.getnframes())
            
            print(f"📊 Audio data size: {len(audio_data)} bytes")
            
            if len(audio_data) == 0:
                raise Exception("No audio data found")
            
            # Process audio in chunks (Vosk best practice)
            chunk_size = 4000  # Process in 4KB chunks
            text_parts = []
            
            for i in range(0, len(audio_data), chunk_size):
                chunk = audio_data[i:i + chunk_size]
                if self.recognizer.AcceptWaveform(chunk):
                    result = self.recognizer.Result()
                    if result:
                        try:
                            result_json = json.loads(result)
                            chunk_text = result_json.get('text', '').strip()
                            if chunk_text:
                                text_parts.append(chunk_text)
                        except json.JSONDecodeError:
                            pass
            
            # Get final result
            final_result = self.recognizer.FinalResult()
            print(f"🎤 Final Vosk result: '{final_result}'")
            
            # Parse final result
            try:
                result_json = json.loads(final_result)
                final_text = result_json.get('text', '').strip()
                print(f"📝 Final parsed text: '{final_text}'")
                
                # Combine all text parts
                all_text = ' '.join(text_parts + [final_text]).strip()
                
                if not all_text:
                    print("⚠️ Warning: Vosk returned empty text")
                    # Try partial results as fallback
                    partial = self.recognizer.PartialResult()
                    print(f"🔄 Partial result: '{partial}'")
                    try:
                        partial_json = json.loads(partial)
                        all_text = partial_json.get('partial', '').strip()
                    except json.JSONDecodeError:
                        pass
                
                return all_text
                
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse Vosk JSON result: {e}")
                print(f"🔍 Raw result was: {final_result}")
                return final_result.strip()
                
        except Exception as e:
            print(f"❌ WAV processing failed: {str(e)}")
            import traceback
            print(f"📋 Full traceback: {traceback.format_exc()}")
            raise Exception(f"WAV processing failed: {str(e)}")
    
    def _transcribe_fallback(self, audio_path: str) -> str:
        """Fallback transcription method with simpler conversion"""
        try:
            print("Using fallback transcription method...")
            
            # Try to load audio with different parameters
            audio_data, sr = librosa.load(audio_path, sr=16000, mono=True, res_type='kaiser_fast')
            
            if len(audio_data) == 0:
                raise ValueError("Empty audio data")
            
            print(f"Fallback audio loaded: {len(audio_data)} samples, {sr} Hz")
            
            # Create WAV file with wave module directly
            import tempfile
            import wave
            import numpy as np
            
            temp_wav = tempfile.mktemp(suffix='.wav')
            
            # Convert to 16-bit PCM
            audio_int16 = (audio_data * 32767).astype(np.int16)
            
            # Write WAV file manually
            with wave.open(temp_wav, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(16000)  # 16kHz
                wav_file.writeframes(audio_int16.tobytes())
            
            print(f"Fallback WAV file created: {temp_wav}")
            
            # Process with Vosk
            return self._process_wav_file(temp_wav)
            
        except Exception as e:
            print(f"Fallback transcription failed: {str(e)}")
            raise Exception(f"Fallback conversion failed: {str(e)}")

    def _convert_to_wav(self, audio_path: str) -> str:
        """Convert audio to WAV format with detailed debugging"""
        print(f"🔄 Converting audio file: {audio_path}")
        
        try:
            # Check if it's already a WAV file
            if audio_path.lower().endswith('.wav'):
                print("✅ File is already WAV format")
                return audio_path
            
            print("🔄 Loading audio with librosa...")
            # Load audio with specific parameters for Vosk
            audio_data, sr = librosa.load(audio_path, sr=16000, mono=True, res_type='kaiser_fast')
            print(f"📊 Loaded audio: {len(audio_data)} samples, {sr} Hz")
            
            if len(audio_data) == 0:
                raise Exception("Empty audio data after loading")
            
            # Create temporary WAV file
            import tempfile
            temp_wav = tempfile.mktemp(suffix='.wav')
            print(f"🔄 Creating temporary WAV file: {temp_wav}")
            
            # Write WAV file with Vosk-compatible format: 16kHz, 16-bit, mono
            print("🔄 Writing WAV file with soundfile...")
            sf.write(temp_wav, audio_data, 16000, subtype='PCM_16', format='WAV')
            print(f"✅ WAV file created successfully")
            
            # Verify the WAV file
            print("🔄 Verifying WAV file format...")
            import wave
            with wave.open(temp_wav, 'rb') as wf:
                channels = wf.getnchannels()
                framerate = wf.getframerate()
                sampwidth = wf.getsampwidth()
                frames = wf.getnframes()
                
                print(f"📊 WAV verification:")
                print(f"   - Channels: {channels} (expected: 1)")
                print(f"   - Sample rate: {framerate} Hz (expected: 16000)")
                print(f"   - Sample width: {sampwidth} bytes (expected: 2)")
                print(f"   - Frames: {frames}")
                print(f"   - Duration: {frames / framerate:.2f} seconds")
                
                if channels != 1 or framerate != 16000 or sampwidth != 2:
                    print("⚠️ Warning: WAV format doesn't match Vosk requirements")
                    # Try to fix the format
                    print("🔄 Attempting to fix WAV format...")
                    return self._fix_wav_format(temp_wav, audio_data)
                else:
                    print("✅ WAV format is correct for Vosk")
            
            return temp_wav
            
        except Exception as e:
            print(f"❌ Audio conversion failed: {str(e)}")
            import traceback
            print(f"📋 Full traceback: {traceback.format_exc()}")
            raise Exception(f"Audio conversion failed: {str(e)}")
    
    def _fix_wav_format(self, wav_path: str, audio_data) -> str:
        """Fix WAV format to match Vosk requirements"""
        try:
            import tempfile
            import wave
            import numpy as np
            
            # Create new WAV file with correct format
            fixed_wav = tempfile.mktemp(suffix='.wav')
            
            # Ensure audio data is in correct range and format
            audio_int16 = (audio_data * 32767).astype(np.int16)
            
            with wave.open(fixed_wav, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(16000)  # 16kHz
                wav_file.writeframes(audio_int16.tobytes())
            
            print(f"✅ Fixed WAV file created: {fixed_wav}")
            return fixed_wav
            
        except Exception as e:
            print(f"❌ Failed to fix WAV format: {str(e)}")
            return wav_path  # Return original if fixing fails