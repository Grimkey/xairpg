import pytest
from unittest.mock import patch
from tictactoe import agent_response, find_player_intent, Intent

# Test cases for player intent detection
@pytest.mark.parametrize(
    "player_prompt, mock_response, expected_intent",
    [
        ("I want to move to position 5", "move", Intent.move),  # Valid move
        ("Where should I move next?", "discuss", Intent.discuss),  # Asking about the board
        ("What is the current board state?", "discuss", Intent.discuss),  # Board discussion
        ("Tell me a joke!", "offtopic", Intent.offtopic),  # Off-topic question
        ("Tell me a tictactoe joke!", "discuss", Intent.discuss),  # Off-topic question
        ("What games are like tictactoe", "discuss", Intent.discuss),  # Off-topic question
        ("I want to place my piece on 99", "error", None),  # Out-of-bounds move (not a valid intent)
    ]
)
@patch("tictactoe.agent_response")  # Mock the agent_response function
def test_find_player_intent(mock_agent_response, player_prompt, mock_response, expected_intent):
    """
    Test find_player_intent with different player prompts and expected intents.
    """

    # Mock the agent response
    #mock_agent_response.return_value = mock_response

    # Call function
    result = find_player_intent(player_prompt)

    # Assert the expected outcome
    assert result == expected_intent

@pytest.mark.parametrize(
    "player_prompt, mock_response, expected_intent",
    [
        ("I want to move to position 5", "move", Intent.move),  # Valid move
        ("Where should I move next?", "discuss", Intent.discuss),  # Asking about the board
        ("What is the current board state?", "discuss", Intent.discuss),  # Board discussion
        ("Tell me a joke!", "offtopic", Intent.offtopic),  # Off-topic question
        ("I want to place my piece on 99", "error", None),  # Out-of-bounds move (not a valid intent)
    ]
)
@patch("tictactoe.agent_response")  # Mock the agent_response function
def test_agent_response(mock_agent_response, player_prompt, mock_response, expected_intent):
    """
    Test find_player_intent with different player prompts and expected intents.
    """

    # Mock the agent response
    #mock_agent_response.return_value = mock_response

    # Call function
    result = agent_response(player_prompt)

    # Assert the expected outcome
    assert result == expected_intent