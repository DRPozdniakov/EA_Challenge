import pygame
import tempfile
import os

def play_audio(audio_data):
    """
    Play audio data directly from memory using pygame
    
    Args:
        audio_data (bytes): The audio data to play
    """
    print(f"Attempting to play audio data of size: {len(audio_data)} bytes")

    # Initialize pygame mixer
    pygame.mixer.init()
    print("Pygame mixer initialized")
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            temp_file.write(audio_data)
            temp_file_path = temp_file.name
        
        # Load and play the audio using pygame
        pygame.mixer.music.load(temp_file_path)
        pygame.mixer.music.play()
        
        # Wait for the audio to finish playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        print("Audio playback completed successfully")
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
    except Exception as e:
        print(f"Error playing audio: {str(e)}")
    finally:
        # Stop any playing audio
        pygame.mixer.music.stop()