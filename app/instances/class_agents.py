from typing import List
from openai import OpenAI
import os
import logging
from dotenv import load_dotenv
import anthropic
from enum import Enum


logger = logging.getLogger(__name__)
class ProcessType:
    INSTRUCT="instruct"
    TTS="tts"
    IMGTOTEXT="img_to_text"
    IMGTOIMG="img_to_img"
class AIModelType(Enum):
    CHATGPT = "CHATGPT"
    QWEN = "QWEN"
    CLAUDE = "CLAUDE"

class MultiModelAgent:
    """
    A class to interact with multiple models (OpenAI, Anthropic, Google) and provide responses. 
    """
    model_type: AIModelType
    model_name: str

    history=[]
    
    def __init__(self, model_name: str, system_prompt: str = None, model_role: str="assistant",
                 logger=None, functions=None, as_json:bool=False, 
                 with_context:bool=False, process_type:ProcessType=ProcessType.INSTRUCT, voice:str="alloy"):

        self.model_name=model_name
        self.system_prompt = [self.message_maker("system", system_prompt)]
        self.model_role = model_role
        self.functions = functions
        self.logger=logger
        self.with_context=with_context
        self.as_json=as_json
        self.process_type=process_type
        self.voice=voice

        dotenv_path = ".env"
        load_dotenv(dotenv_path)

        if "gpt" or "tts" in model_name.lower():
            api_key = os.getenv('OPENAI_AI_KEY')
            self.client_model = OpenAI(api_key=api_key)
            self.model_type = AIModelType.CHATGPT

        elif "claude" in model_name.lower():
            anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
            self.client_model  = anthropic.Anthropic(api_key=anthropic_api_key)
            self.model_type = AIModelType.CLAUDE
        
        elif "qwen" in model_name.lower():
            api_key = os.getenv('QWEN_AI_KEY')
            self.client_model=OpenAI(
        api_key=os.getenv("QWEN_AI_KEY"), # If you have not configured the environment variable, replace DASHSCOPE_API_KEY with your API key
        base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",  # Replace https://dashscope-intl.aliyuncs.com/compatible-mode/v1 with the base_url of the DashScope SDK
            )
            self.model_type = AIModelType.QWEN

        else:
            raise ValueError(f"Unrecognized model: {model_name}")

        self.logger.info(f"Model {model_name} initialized")
    
    @staticmethod
    def message_maker(role: str, content: str) -> dict:
        """
        Create a message dictionary for the model.
        """
        return {"role": role, "content": content}
    
    @staticmethod
    def message_maker_tts(role: str, content: str, voice: str) -> dict:
        """
        Create a message dictionary for the model.
        """
        return {"role": role, "input": content, "voice": voice}

    def add_system_prompt(self,system_prompt:str):
        self.system_prompt.append(self.message_maker("system", system_prompt))
    
    async def assist_user(self, question: str, temperature: float = 0.5, max_tokens: int =500, top_p=0.7, seed: int = 69):
        
        self.logger.info(f"Model {self.model_role} asked: \n {question}")

        if self.model_type == AIModelType.CHATGPT or self.model_type == AIModelType.QWEN:
            
            if self.process_type == ProcessType.INSTRUCT:
                if self.with_context:
                    content = [system_message for system_message in self.system_prompt]  + self.history + [{"role":"user","content":question}]
                else:
                    content = [system_message for system_message in self.system_prompt] + [self.message_maker("user", question)]

        result = self.client_model.chat.completions.create(
                    model=self.model_name,
                    messages=content,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p,
                    seed=seed
                    )
        answer=result.choices[0].message.content

        # Storing conversation history to keep context of conversation
        if self.with_context:
            self.history = self.history + [
                                    {"role": "user",      "content": question},
                                    {"role": "assistant", "content": answer}
                                ]
            
        logger.debug(f"Model {self.model_role} answered: \n {answer}")

        return [{"role": f"{self.model_role}"},{"content" : answer}]