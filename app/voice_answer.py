import os
import logging
import io
import tempfile
import pygame
import asyncio
from openai import OpenAI
from dotenv import load_dotenv

from instances.class_agents import MultiModelAgent, ProcessType

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class TTSAgent:
    def __init__(self,logger=None):
        self.logger=logger
        self.model_tts_converter="gpt-4o-mini-tts"
        self.agent_tts_converter=MultiModelAgent(model_name=self.model_tts_converter, 
                                                 process_type=ProcessType.TTS, 
                                                 logger=self.logger)
        # Initialize pygame mixer
        pygame.mixer.init()
        self.logger.debug("Pygame mixer initialized")

    async def transform_text_to_speech(self, text: str, voice:str="nova"):
        response = await self.agent_tts_converter.client_model.audio.speech.create(
            model=self.model_tts_converter,
            voice=voice,
            input=text
        )
        return response

    def play_audio(self, audio_data):
        """
        Play audio data directly from memory using pygame
        
        Args:
            audio_data (bytes): The audio data to play
        """
        self.logger.debug(f"Attempting to play audio data of size: {len(audio_data)} bytes")
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

    def text_to_speech(self, text, voice="alloy"):
        """
        Convert text to speech using OpenAI's TTS API and return the audio data
        
        Args:
            text (str): The text to convert to speech
            voice (str): The voice to use (options: alloy, echo, fable, onyx, nova, shimmer)
        
        Returns:
            bytes: The audio data
        """
        self.logger.debug(f"Starting text-to-speech conversion with voice: {voice}")
        self.logger.debug(f"Text length: {len(text)} characters")
        
        try:
            # Generate speech
            self.logger.debug("Sending request to OpenAI TTS API")
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text
            )
            self.logger.debug("Received response from OpenAI TTS API")
            
            # Get the audio data
            audio_data = response.content
            self.logger.debug(f"Retrieved audio data: {len(audio_data)} bytes")
            return audio_data
            
        except Exception as e:
            self.logger.error(f"An error occurred during text-to-speech conversion: {str(e)}")
            return None

class VoiceAnswer:

    def __init__(self,logger=None):
        self.logger=logger

        # self.model_assistant="qwen2.5-7b-instruct"
        self.model_assistant="gpt-4.1"
        system_prompt_assistant = """
        You are a helpful smart and pleasant assitant intended to kindly answer 
        any kind of question with versile literature erudition and light futuristic touch.
        """
        self.agent_assistant=MultiModelAgent(system_prompt=system_prompt_assistant, 
                                             model_name=self.model_assistant, logger=self.logger, 
                                             process_type="instruct", with_context=True)

        self.tts_agent=TTSAgent(logger=self.logger)

    def get_answer(self):
        return self.answer

    def set_answer(self, answer: str):
        self.answer = answer

    async def get_voice_answer(self):
        # 1. Get the question from the user b source of the choice
        question = "How much is the fish?"

        # 2. Send the question OpenAI Model. The choice is to keep conversation context for this models instance
        answer = await self.agent_assistant.assist_user(question=question)
        self.logger.info(f"{self.model_assistant} answer is: {answer}")

        # 3. Send answer via TCP socket to the external service for evaluation
        answer_tts = await self.tts_agent.transform_text_to_speech(answer[1]["content"])
        self.tts_agent.play_audio(audio_data=answer_tts.content)

        print(answer)

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger(__name__)
    logger = logging.getLogger(__name__)
    voice_answer = VoiceAnswer(logger)
    asyncio.run(voice_answer.get_voice_answer())
