import json
from ollama import chat

from src.ai_call import AIModel
from src.npc import NPC

# Step 1: Read the NPC JSON from file
with open('prompts/npc_prompt.txt', 'r') as file:
    npc_data = file.read() 

npc_data = NPC.create(npc_data, AIModel())
file_name = f'game/{npc_data.name.lower().replace(" ", "_")}.json'
npc_data.to_file(file_name)
print(npc_data.model_dump_json())