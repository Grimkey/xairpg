from src.npc import NPC
from src.ai_call import AIModel, Message


def main():
    def do_stuff(msg: str):
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
          print(chunk['message']['content'], end='', flush=True)

    ai_model = AIModel()
    print("Loading NPC")
    npc_data = NPC.from_file('npcs/marlena_graves.json')

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
        print(chunk['message']['content'], end='', flush=True)

    print("------------------------------------------------------") 
    print("Press Enter to perform an action. Type 'quit' to exit.")
    while True:
        # Prompt the user for input
        user_input = input(">> ")
        
        # Check if the user wants to quit
        if user_input.lower() == "quit":
            print("Exiting program. Goodbye!")
            break

        # Call the do_stuff function
        do_stuff(user_input)

if __name__ == "__main__":
    main()