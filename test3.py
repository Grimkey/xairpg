import json
from ollama import chat

from src.ai_call import AIModel, Message
from src.npc import NPC

# Step 1: Read the NPC JSON from file
with open('prompts/planner.txt', 'r') as file:
    npc_data = file.read() 

msg = Message(
    role='user',
    content=npc_data
)
stream = AIModel().chat([msg])
for chunk in stream:
    print(chunk['message']['content'], end='', flush=True)