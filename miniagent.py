import json
from ollama import chat, ChatResponse
from pydantic import BaseModel

def default_chat(system_prompt: str, user_prompt: str) -> str:
    response: ChatResponse = chat(
            model='llama3.2',
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
    return response.message.content


class AgentConfig(BaseModel):
    system_prompt: str
    invoke_func: callable[[str, str], str] = default_chat
    retries: int = 3


class Agent:
    def __init__(self, config: AgentConfig):
        self.system_prompt = config.system_prompt
        self.invoke_func = config.invoke_func
        self.retries = config.retries
        self.fail_count = 0

    def invoke(self, user_prompt: str) -> dict:
        response = self.invoke_func(self.system_prompt, user_prompt)

        if self.fail_count >= self.retries:
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                self.fail_count += 1
                if self.fail_count >= self.retries:
                    return {"error": "Failed to parse response."}
        
        

