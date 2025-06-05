"""
agent_tss.py
-----------
TTSAgent for converting text to speech using LLM APIs.
"""

import logging
from typing import Optional, Dict, Any, List, Union
from app.agents.class_agents import MultiModelAgent, ProcessType

class TTSAgent:
    """
    TTSAgent handles text-to-speech conversion using a specified model.
    """
    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        """
        Initialize the TTSAgent.

        Args:
            logger (Optional[logging.Logger]): Logger instance.
        """
        self.logger = logger or logging.getLogger(__name__)
        self.model_tts_converter = "gpt-4o-mini-tts"
        self.agent_tts_converter = MultiModelAgent(
            model_name=self.model_tts_converter,
            process_type=ProcessType.TTS,
            logger=self.logger
        )

    async def transform_text_to_speech(self, text: str, voice: str = "nova") -> Optional[bytes]:
        """
        Convert text to speech asynchronously using the TTS model.

        Args:
            text (str): The text to convert.
            voice (str): The voice to use for TTS.

        Returns:
            Optional[bytes]: The audio data.
        """
        response = self.agent_tts_converter.client_model.audio.speech.create(
            model=self.model_tts_converter,
            voice=voice,
            input=text
        )
        # Get the raw audio data
        audio_data = response.content
        return audio_data

    def text_to_speech(self, text: str, voice: str = "nova") -> Optional[bytes]:
        """
        Convert text to speech using OpenAI's TTS API and return the audio data.

        Args:
            text (str): The text to convert to speech.
            voice (str): The voice to use (options: alloy, echo, fable, onyx, nova, shimmer).

        Returns:
            Optional[bytes]: The audio data.
        """
        self.logger.debug(f"Starting text-to-speech conversion with voice: {voice}")
        self.logger.debug(f"Text length: {len(text)} characters")

        try:
            # Generate speech
            self.logger.debug("Sending request to OpenAI TTS API")
            response = self.agent_tts_converter.client_model.audio.speech.create(
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
