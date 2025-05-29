import os
import logging

import asyncio

from app.instances.class_agents import MultiModelAgent, ProcessType
from app.interfaces.tcp_server import TCPServer    
from app.agents.agent_tss import TTSAgent

class VoiceAnswerService:

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
                                             process_type=ProcessType.INSTRUCT, with_context=True)

        self.tts_agent=TTSAgent(logger=self.logger)

        self.tcp_server = TCPServer(host='0.0.0.0', port=8888, logger=self.logger)

    def get_answer(self):
        return self.answer

    def set_answer(self, answer: str):
        self.answer = answer

    async def get_voice_answer(self):
        self.logger.info("Starting voice answer service...")
        # Start server in a separate task

         # 1. Initialize the server to listen for the incomeing question
        server_task = asyncio.create_task(self.tcp_server.start())
        self.running = True
        self.logger.info("Server started, waiting for messages...")

        while self.running:
            if self.tcp_server.received_message:
                # 2. On receive of the question process it via LLM model and receive the text answer
                # question = "How much is the fish?"
                self.logger.info(f"Starting to process message: {self.tcp_server.received_message} from {self.tcp_server.client_address}")

                answer = await self.agent_assistant.assist_user(question=self.tcp_server.received_message)
                self.logger.info(f"{self.model_assistant} answer is: {answer}")

                # 3. Send the LLM answer to the TTS agent to convert to audio
                audio_data = await self.tts_agent.transform_text_to_speech(answer[1]["content"])
                self.logger.info(f"Generated audio data: {len(audio_data)} bytes")
                
                # Play audio for test purposes
                # self.tts_agent.play_audio(audio_data=audio_data)

                # 4. Return audio to the client which has initialzed the request
                status = self.tcp_server.send_message(answer=audio_data, address=self.tcp_server.client_address)

                if status:
                    self.logger.info(f"Audio data sent to client {self.tcp_server.client_address} with status {status}")
                else:
                    self.logger.error(f"Failed to send audio data to client {self.tcp_server.client_address} with status {status}")

                # Clear the received message after processing
                self.tcp_server.received_message = None
                self.logger.info("Message processing completed")
            else:
                self.logger.debug("No new messages, waiting...")

            await asyncio.sleep(2)

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger(__name__)
    voice_answer = VoiceAnswerService(logger)
    asyncio.run(voice_answer.get_voice_answer())
