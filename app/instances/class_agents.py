from typing import List
from openai import OpenAI
import os
import logging
from dotenv import load_dotenv
import anthropic
from enum import Enum


logger = logging.getLogger(__name__)

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
    
    def __init__(self, system_prompt: str, model_name: str, model_role: str="assistant",
                 logger=None, functions=None, as_json:bool=False, 
                 with_context:bool=False, with_data_url:bool=False, with_attachement:bool=False):

        self.model_name=model_name
        self.system_prompt = [self.message_maker("system", system_prompt)]
        self.model_role = model_role
        self.functions = functions
        self.logger=logger
        self.with_context=with_context
        self.as_json=as_json

        dotenv_path = ".env"
        load_dotenv(dotenv_path)

        if "gpt" in model_name.lower():
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
    def message_maker_with_attachement(role: str, content: str, attachments: list[dict]) -> dict:
        """
        Create a message dictionary for the model.
        """
        return {"role": role, "content": content, "attachments" : [
            {"filename" : attach["filename"], "data": attach["data"]} for attach in attachments
        ]}
    
    @staticmethod
    def message_maker_with_data_url(role: str, content: str, attachments: list[dict]) -> dict:
        """
        Create a message dictionary for the model.
        """
        return {"role": role, "content": [
            {"type": "text", "text": content},
            {"type": "image_url", "image_url": {"url": f"{attachments[0]['data']}"}}
            ]}

    def add_system_prompt(self,system_prompt:str):
        self.system_prompt.append(self.message_maker("system", system_prompt))
    
    async def assist_user(self, question: str, temperature: float = 0.5, max_tokens: int =500, top_p=0.7, seed: int = 69):
        
        self.logger.debug(f"Model {self.model_role} asked: \n {question}")

        if self.model_type == AIModelType.CHATGPT or self.model_type == AIModelType.QWEN:

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

        elif self.model_type == AIModelType.CLAUDE:
            system_prompt_combined = "\n\n".join([prompt["content"] for prompt in self.system_prompt]) 

            content=[self.message_maker("user", question)]
            result = self.client_model.messages.create(
                model=self.model_name,
                system=system_prompt_combined,
                messages=content,
                temperature=temperature,
                max_tokens=max_tokens
            )
            answer=result.content[0].text
        
        if self.with_context:
            self.history = self.history + [
                                    {"role": "user",      "content": question},
                                    {"role": "assistant", "content": answer}
                                ]
            

        logger.debug(f"Model {self.model_role} answered: \n {answer}")

        return [{"role": f"{self.model_role}"},{"content" : answer}]