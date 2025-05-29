import asyncio
import logging
import pygame
import tempfile
import os

class TCPClient:
    def __init__(self, host='localhost', port=8888, logger=None):
        self.host = host
        self.port = port
        self.logger = logger
        # Initialize pygame mixer
        pygame.mixer.init()
        self.logger.debug("Pygame mixer initialized")

    async def send_question(self, question):
        """Send a question to the server and receive audio response"""
        try:
            # Connect to server
            reader, writer = await asyncio.open_connection(self.host, self.port)
            self.logger.info(f"Connected to server at {self.host}:{self.port}")
            
            # Send question
            writer.write(question.encode())
            await writer.drain()
            self.logger.info(f"Sent question: {question}")
            
            # Receive audio data with end marker
            audio_data = bytearray()
            end_marker = b"<END_OF_AUDIO>"
            
            while True:
                chunk = await reader.read(1024*1024)  # Read in 1MB chunks
                if not chunk:
                    break
                    
                # Check if end marker is in this chunk
                if end_marker in chunk:
                    # Split at end marker and add only the audio data
                    audio_data.extend(chunk.split(end_marker)[0])
                    break
                else:
                    audio_data.extend(chunk)
            
            self.logger.info(f"Received complete audio data: {len(audio_data)} bytes")
            
            # Play the audio
            self.play_audio(audio_data)
            
        except Exception as e:
            self.logger.error(f"Error in client: {str(e)}")
        finally:
            writer.close()
            await writer.wait_closed()
            self.logger.info("Connection closed")

    def play_audio(self, audio_data):
        """Play received audio data"""
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            self.logger.debug(f"Created temporary file: {temp_file_path}")
            
            # Load and play the audio using pygame
            pygame.mixer.music.load(temp_file_path)
            pygame.mixer.music.play()
            
            # Wait for the audio to finish playing
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            self.logger.info("Audio playback completed successfully")
            
            # Clean up the temporary file
            os.unlink(temp_file_path)
            self.logger.debug("Temporary file cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error playing audio: {str(e)}")
        finally:
            # Stop any playing audio
            pygame.mixer.music.stop()

async def main():
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger(__name__)
    
    # Create client and send question
    client = TCPClient(logger=logger)
    question = "How much is the fish?"
    await client.send_question(question)

if __name__ == "__main__":
    asyncio.run(main()) 