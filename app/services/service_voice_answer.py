"""
voice_answer.py
--------------
Main service for handling voice-based answers using LLM and TTS.
"""
import logging

from app.interfaces.websocket_server import WebSocketServer
from app.agents.class_agents import MultiModelAgent, ProcessType
from app.agents.agent_tss import TTSAgent


class VoiceAnswerService:
    system_prompt_assistant = (
            """
            You are a helpful smart and pleasant assistant intended to kindly answer 
            any kind of question with versatile literature erudition and light futuristic touch.
            """
            )
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.model_assistant = "gpt-4.1"

        self.agent_assistant = MultiModelAgent(
            system_prompt=self.system_prompt_assistant,
            model_name=self.model_assistant,
            logger=self.logger,
            process_type=ProcessType.INSTRUCT,
            with_context=True
        )
        self.tts_agent = TTSAgent(logger=self.logger)
        self.server = WebSocketServer(
            host='0.0.0.0',
            port=8888,
            logger=self.logger,
            handler=self.handle_message
        )

    async def handle_message(self, websocket, message):
        # 1. Receiving the message from the socket
        self.logger.info(f"Received message: {message}")
        # 2. Get answer from LLM in the text format
        answer = await self.agent_assistant.assist_user(question=message)
        # 3. Convert answer to audio on the external service
        audio_data = await self.tts_agent.transform_text_to_speech(answer[1]["content"])
        # 4. Send audio back to the client
        await websocket.send(audio_data)
        self.logger.info("Audio data sent to client.")

    async def run(self):
        await self.server.start()
