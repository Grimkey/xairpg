import json
from ollama import chat
from pydantic import BaseModel, ValidationError
import argparse
from enum import Enum
from typing import Iterator, Optional
import logging
import time

# Configure logging
logging.basicConfig(
    filename="app.log",  # Log file name
    level=logging.DEBUG,  # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
    datefmt="%Y-%m-%d %H:%M:%S",  # Date format
)

agent_context_prompt = """
    You are a tic tac toe agent. The human player goes first and plays as X. You are playing as O. 
"""

class Move(BaseModel):
    player: str
    move: int

class Intent(str, Enum):
    move = "move"
    discuss = "discuss"
    offtopic = "offtopic"


class PlayerIntent(BaseModel):
    intent: Intent
    move: Optional[Move] = None
    message: Optional[str] = None


class Result(BaseModel):
    """
    A model representing the current state of a Tic-Tac-Toe game.

    Attributes:
        X (list[int]): A list of integers (1-9) representing positions occupied by player X. 
            These positions are mutually exclusive from the `O` and `empty` lists.
        O (list[int]): A list of integers (1-9) representing positions occupied by player O. 
            These positions are mutually exclusive from the `X` and `empty` lists.
        empty (list[int]): A list of integers (1-9) representing unoccupied positions on the board. 
            These positions are mutually exclusive from the `X` and `O` lists.
        winner (str): A string indicating the winner of the game. 
            Possible values:
                - "X": Player X has won the game.
                - "O": Player O has won the game.
                - " ": The game is still ongoing (no winner yet).
        error (str): A string containing error information if a move was not accepted.
            - An empty string ("") indicates the move was accepted.
            - Otherwise, it contains details about what the error was.
    """
    X: list[int]
    O: list[int]
    empty: list[int]
    winner: str
    error: str = ""

    def print_board(self) -> str:
        # Flatten the board into a single array
        symbols_board = [str(i) if i in self.empty else "X" if i in self.X else "O" for i in range(1, 10)]
        board = ""
        for i in range(0, 9, 3):
            board += (" | ".join(symbols_board[i:i+3])) + "\n"
            if i < 6:
                board += "-" * 10 + "\n"
        return board


def rules_prompt(board: Result) -> str:
    board_json = board.model_dump_json()

    orig_rules_prompt = f"""
        {agent_context_prompt} The board has values 1 to 9.  

        The possible winning conditions are:

        {{"X"=[1, 2, 3]}}, {{"X"=[4, 5, 6]}}, {{"X"=[7, 8, 9]}}, {{"X"=[1, 4, 7]}}, {{"X"=[2, 5, 8]}}, {{"X"=[3, 6, 9]}}, {{"X"=[1, 5, 9]}}, {{"X"=[3, 5, 7]}}
    
        The board is represented as follows:
        {board_json}
        """
    
    return orig_rules_prompt


def find_player_intent(player_prompt: str, max_retries: int = 3, retry_delay: float = 1.0) -> Optional[Intent]:
    prompt = f"""
    {agent_context_prompt}

    Given the prompt below, determine the player's intended outcome. There are three possible intents:

    1. "move": The player is making a move on the board. If it is a single number that is the intended move square. Questions are not considered moves. Selecting a square or moving to a square is considered a move.
    2. "discuss": The player is discussing the game or asking questions. These include questions about where to move next or the current board state.
    3. "offtopic": The player is discussing something unrelated to the game.

    prompt: {player_prompt}

    determine which ones of these applies and provide a one word answer.

"""

    for attempt in range(max_retries):
        try:
            response = agent_response(prompt).lower().replace("'","").replace("\"","").strip()
            
            # Validate the response
            if response in Intent.__members__.values():
                return Intent(response)
            else:
                logging.warning(f"Invalid response from agent: '{response}'. Retrying... ({attempt+1}/{max_retries})")

        except ValueError as e:
            logging.error(f"Error parsing intent: {e}. Retrying... ({attempt+1}/{max_retries})")

        time.sleep(retry_delay)  # Wait before retrying

    logging.error("All retries failed. Returning None.")
    return None

def response_offtopic_intent(player_prompt: str) -> str:
    return_prompt = f"""
    The player prompt was: {player_prompt}

    Explain concisely why this prompt is off-topic.
    """
    logging.debug(f"Off-topic prompt: {return_prompt}")

    response = agent_response(return_prompt)
    logging.debug(f"Off-topic response: {response}")
    return response

def response_discussion_intent(player_prompt: str, board: Result) -> str:
    return_prompt = f"""
    {rules_prompt(board) }

    The player prompt was: {player_prompt}

    Draw the board for the player then focus on the game rules and the current board state. What is your response?
    """
    logging.debug(f"Discussion prompt: {return_prompt}")
 
    response = agent_response(return_prompt)
    logging.debug(f"Discussion response: {response}")
    return response

def response_move_intent(player_prompt: str, board: Result, max_retries: int = 3, retry_delay: float = 1.0) -> str:
    move_rules = """
        You can only pick from the " " list of the current board. What is your next move?

        Return your move as JSON with no markdown. For example, if you want to move to position 1, return {{"move": 1}}.
"""
    return_prompt = f"""
    {rules_prompt(board) }

    The player prompt was: {player_prompt}

    {move_rules}    
"""
    logging.debug(f"Move prompt: {return_prompt}")
 
    response = agent_response(return_prompt)
    logging.debug(f"Move response: {response}")
    return response

    for attempt in range(max_retries):
        try:
            response = agent_response(return_prompt).strip()
            logging.debug(f"Move response: {response}")

            # Validate the response
            if response in Intent.__members__.values():
                return Move.model_validate_json(response)
            else:
                logging.warning(f"Invalid response from agent: '{response}'. Retrying... ({attempt+1}/{max_retries})")

        except ValidationError as e:
            logging.error(f"Error parsing intent: {e}. Retrying... ({attempt+1}/{max_retries})")

        time.sleep(retry_delay)  # Wait before retrying

    logging.error("All retries failed. Returning None.")
    return None

situation_player_move = """
    You are playing as X. What is your move?

    - Analyze the current board state.
    - Make your move.
    - Return your move as JSON without any markdown. For example, {{"player": "X", "move": 1}}.
"""

situation_agent_move = """
    You are playing as O. What is your move?

    - Analyze the current board state.
    - Make your move.
    - Return your move as JSON without any markdown. For example, {{"player": "O", "move": 1}}.
"""

def agent_prompt(situation: str, board: Result) -> str:
    board_json = board.model_dump_json()

    rules_prompt = f"""
    You are a Tic Tac Toe agent playing interactively with a human player. The human player goes firth and is always "X" and you are always "O". The board has values from 1 to 9.

    The possible winning conditions are:
    [1, 2, 3], [4, 5, 6], [7, 8, 9], [1, 4, 7], [2, 5, 8], [3, 6, 9], [1, 5, 9], [3, 5, 7]

    The board is represented as a dictionary:
    {{"X": [positions occupied by X], "O": [positions occupied by O], "empty": [positions that are still empty]}}.

    The game flow:
    1. The human player (O) makes the first move by providing a position (1-9) from the " " list.
    2. You (X) respond with your move, always picking from the " " list.
    3. The game alternates between the human player and you until there is a winner or the game ends in a draw.

    Rules:
    - You must only pick moves from the "empty" list.
    - You must always prioritize winning if possible.
    - If you cannot win in this move, block the opponent if they are about to win.
    - Otherwise, choose the best available position strategically.

    The board is currently:
    {board_json}
    """

    return f"""
    {rules_prompt}

    Current board is:
    {board.print_board()}
    """

def agent_iterator(content: str) -> Iterator[str]:
    """Generator that yields streamed messages from the chat model."""
    user_message = {
        'role': 'user',
        'content': content,
    }

    stream = chat(
        model='llama3.2',
        messages=[user_message],
        stream=True,
    )

    for chunk in stream:
        yield chunk['message']['content']


def agent_response(content: str) -> str:
    """Collects the output of agent_call_iterator into a single string."""
    return "".join(agent_iterator(content))


def print_agent_call(content: str):
    user_message = {
        'role': 'user',
        'content': content,
    }


    stream = chat(
        model='llama3.2',
        messages=[user_message],
        stream=True,
    )

    for chunk in stream:
        print(chunk['message']['content'], end='', flush=True)


class TicTacToe:
    def __init__(self):
        self.board = [" " for _ in range(9)]
        self.players = ["X", "O"]
        self.turn = 0

    def validate_move(self, move: Move) -> str:
        if move.player not in self.players:
            return "Invalid player."
        if move.move < 1 or move.move > 9:
            return "Move must be between 1 and 9."
        if self.board[move.move - 1] != " ":
            return "Cell is already occupied."
        if self.players[self.turn % 2] != move.player:
            return "Not your turn."
        return ""

    def update_board(self, move: Move):
        self.board[move.move - 1] = move.player
        self.turn += 1

    def get_result(self) -> Result:
        X_positions = [i + 1 for i, cell in enumerate(self.board) if cell == "X"]
        O_positions = [i + 1 for i, cell in enumerate(self.board) if cell == "O"]
        empty_positions = [i + 1 for i, cell in enumerate(self.board) if cell == " "]

        winner = self.check_winner()

        return Result(
            X=X_positions,
            O=O_positions,
            empty=empty_positions,
            winner=winner if winner else " ",
            error=""
        )

    def check_winner(self) -> str:
        winning_combinations = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]             # Diagonals
        ]

        for combo in winning_combinations:
            if self.board[combo[0]] == self.board[combo[1]] == self.board[combo[2]] != " ":
                return self.board[combo[0]]
        return None

    def play(self, move: Move) -> Result:
        error = self.validate_move(move)
        if error:
            return Result(
                X=[i + 1 for i, cell in enumerate(self.board) if cell == "X"],
                O=[i + 1 for i, cell in enumerate(self.board) if cell == "O"],
                empty=[i + 1 for i, cell in enumerate(self.board) if cell == " "],
                winner=" ",
                error=error
            )

        self.update_board(move)
        return self.get_result()
    
    #def print_board(self):
    #    for i in range(0, 9, 3):
    #        print(" | ".join(self.board[i:i+3]))
    #        if i < 6:
    #            print("-" * 10)

def game_agent():
    game = TicTacToe()

    while True:
        result = game.get_result()

        prompt = input("> ")
        intent = find_player_intent(prompt)
        if intent == Intent.move:
            move = Move(player="X", move=5)
            result = game.play(move)
            if result.error:
                print(f"Error: {result.error}")
                continue
            print(result.print_board())
        elif intent == Intent.discuss:
            print(response_discussion_intent(prompt, result))
            continue
        elif intent == Intent.offtopic:
            print(response_offtopic_intent(prompt))


def game_manual():
    game = TicTacToe()
    player = 0
    while True:
        # Check if there is a winner or a draw
        result = game.get_result()

        # Print the current board
        print("\nCurrent board:")
        print(result.print_board())

        if result.winner != " ":
            print(f"Game over! Winner: {result.winner}")
            break
        if not result.empty:
            print("Game over! It's a draw.")
            break

        # Player X move
        try:
            piece = ["X", "O"][player]
            player_move = int(input(f"{piece} move (1-9): "))
            player_result = game.play(Move(player=piece, move=player_move))
            if player_result.error:
                print(f"Error: {player_result.error}")
                continue
            print(f"Board: {player_result}")
            player = 0 if player == 1 else 1
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 9.")
            continue



def main():
    parser = argparse.ArgumentParser(description="Tic Tac Toe Game")
    parser.add_argument("--manual", action="store_true", help="Play in manual mode (two players)")
    args = parser.parse_args()

    mode = "manual" if args.manual else "agent"
    print(f"Starting Tic Tac Toe in {mode} mode.")
    if mode == "manual":
        game_manual()
    else:
        game_agent()


if __name__ == "__main__":
    main()

