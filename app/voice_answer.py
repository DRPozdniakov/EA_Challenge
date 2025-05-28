from instances.class_agents import MultiModelAgent
import asyncio
import logging

class VoiceAnswer:
    system_prompt = """
    You are a helpful smart and pleasant assitant intended to kindly answer any kind of question with versile literature erudition and light futuristic touch.
    """

    def __init__(self,logger=None):
        self.logger=logger
        self.model_assistant="qwen2.5-7b-instruct"
        self.agent_assistant=MultiModelAgent(system_prompt=self.system_prompt, model_name=self.model_assistant, logger=self.logger, with_context=True)

    def get_answer(self):
        return self.answer

    def set_answer(self, answer: str):
        self.answer = answer

    async def get_voice_answer(self):
        # 1. Get the question from the user b source of the choice
        question = "How much is the fish?"

        # 2. Send the question OpenAI Model. The choice is to keep conversation context for this models instance
        response = await self.agent_assistant.assist_user(question=question)

        print(response[1]["content"])

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    voice_answer = VoiceAnswer(logger)
    asyncio.run(voice_answer.get_voice_answer())
