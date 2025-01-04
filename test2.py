import json
from ollama import chat

from src.npc import NPC
from src.ai_call import Message, AIModel

npc_data = NPC.from_file('npcs/marlena_graves.json')

system_message = Message(
    role='system',
    content=f"""
You are roleplaying as the NPC Marlene Graves. Here is her profile:

{npc_data.model_dump_json()}

Based on this information, describe what happens when the player walks into Marlene's shop. Provide details about her appearance, the shop, her initial attitude toward the player, and anything she might say or do.
"""
)


user_message = Message(
    role='user',
    content="Describe Marlene when the player walks into her shop."
)

ai_model = AIModel()
stream = ai_model.chat([system_message, user_message])

for chunk in stream:
    print(chunk['message']['content'], end='', flush=True)