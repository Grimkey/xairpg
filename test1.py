import json
from ollama import chat


# Step 3: Set up the user context
user_message = {
    'role': 'user',
    'content': """
        You are a tic tac toe agent. The human player goes first and plays as X. You are playing as O. The board has values 1 to 9.

        Given the prompt below, determine the player's intended outcome. There are three possible intents:

        1. "move": The player is making a move on the board.
        2. "discuss": The player is discussing the game or asking questions.
        3. "offtopic": The player is discussing something unrelated to the game.

        prompt: I want to move to position 5

        determine which ones of these applies and provide a one word answer.
""",
}


stream = chat(
    model='llama3.2',
    messages=[user_message],
    stream=True,
)

# Step 5: Print the response as it streams
for chunk in stream:
    print(chunk['message']['content'], end='', flush=True)