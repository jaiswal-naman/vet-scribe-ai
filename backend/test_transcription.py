#!/usr/bin/env python3
"""
Test script to debug transcription issues
"""

import os
import sys
import tempfile
import wave
import numpy as np

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_audio_processing():
    """Test basic audio processing capabilities"""
    print("Testing audio processing...")
    
    try:
        import librosa
        print("✅ librosa imported successfully")
    except ImportError as e:
        print(f"❌ librosa import failed: {e}")
        return False
    
    try:
        import soundfile as sf
        print("✅ soundfile imported successfully")
    except ImportError as e:
        print(f"❌ soundfile import failed: {e}")
        return False
    
    try:
        import vosk
        print("✅ vosk imported successfully")
    except ImportError as e:
        print(f"❌ vosk import failed: {e}")
        return False
    
    # Test creating a simple audio file
    try:
        # Create a simple sine wave
        sample_rate = 16000
        duration = 1.0  # 1 second
        frequency = 440  # A4 note
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio_data = 0.3 * np.sin(2 * np.pi * frequency * t)
        
        # Save as WAV
        temp_wav = tempfile.mktemp(suffix='.wav')
        sf.write(temp_wav, audio_data, sample_rate, subtype='PCM_16')
        
        print(f"✅ Created test WAV file: {temp_wav}")
        
        # Verify the file
        with wave.open(temp_wav, 'rb') as wf:
            print(f"✅ WAV file verified: {wf.getnchannels()} channels, {wf.getframerate()} Hz, {wf.getsampwidth()} bytes/sample")
        
        # Clean up
        os.remove(temp_wav)
        print("✅ Test audio file cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Audio processing test failed: {e}")
        return False

def test_vosk_model():
    """Test Vosk model loading"""
    print("\nTesting Vosk model...")
    
    try:
        from app.transcription import VoskTranscriber
        
        transcriber = VoskTranscriber()
        
        if transcriber.model_loaded:
            print("✅ Vosk model loaded successfully")
            return True
        else:
            print("❌ Vosk model failed to load")
            return False
            
    except Exception as e:
        print(f"❌ Vosk model test failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Transcription Debug Test ===\n")
    
    audio_ok = test_audio_processing()
    vosk_ok = test_vosk_model()
    
    print(f"\n=== Results ===")
    print(f"Audio processing: {'✅ OK' if audio_ok else '❌ FAILED'}")
    print(f"Vosk model: {'✅ OK' if vosk_ok else '❌ FAILED'}")
    
    if audio_ok and vosk_ok:
        print("\n🎉 All tests passed! Transcription should work.")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.") 