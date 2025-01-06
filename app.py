from src.npc import NPC
from src.ai_call import AIModel, Message


def main():  
    context = ""

    def do_stuff(msg: str, context: str) -> str:
      """
      This function will be called after the player hits enter.
      Replace this code with whatever action you want to perform.
      """
      user_message = Message(
          role='user',
          content=msg,
      )
      stream = ai_model.chat([system_message, user_message])

      for chunk in stream:
          part = chunk['message']['content']
          context += part
          print(part, end='', flush=True)

      return context

    ai_model = AIModel()
    print("Loading NPC")
    npc_data = NPC.from_file('game/marlena_graves.json')

    system_message = Message(
    role='user',
    content=f"""
You are roleplaying as the NPC Marlene Graves. Here is her profile:

{npc_data.model_dump_json()}

Based on this information, describe what happens when the player walks into Marlene's shop. Provide details about her appearance, the shop, her initial attitude toward the player, and anything she might say or do.
"""
)
    stream = ai_model.chat([system_message])

    for chunk in stream:
        part = chunk['message']['content']
        context += part
        print(part, end='', flush=True)

    print("------------------------------------------------------") 
    print("Press Enter to perform an action. Type 'quit' to exit.")
    while True:
        # Prompt the user for input
        user_input = input(">> ")
        
        # Check if the user wants to quit
        if user_input.lower() == "quit":
            print("Exiting program. Goodbye!")
            break
        # Check if the user wants to quit
        if user_input.lower() == "context":
            print(context)
            continue
        
        # Call the do_stuff function
        context = do_stuff(user_input, context)

if __name__ == "__main__":
    main()