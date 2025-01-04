import json
from ollama import chat


# Step 3: Set up the user context
user_message = {
    'role': 'user',
    'content': "Can you do text"
}


stream = chat(
    model='llama3.2',
    messages=[user_message],
    stream=True,
)

# Step 5: Print the response as it streams
for chunk in stream:
    print(chunk['message']['content'], end='', flush=True)