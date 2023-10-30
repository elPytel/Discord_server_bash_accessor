# By Pytel

import os
import asyncio
import async_timeout

def pipe_is_empty(pipe_path: str) -> bool:
    try:
        if os.path.exists(pipe_path):
            return os.path.getsize(pipe_path) == 0
        else:
            print(f"Pipe '{pipe_path}' does not exist.")
            return True  # Pipe does not exist or cannot be accessed
    except Exception as e:
        print(f"Error while checking pipe '{pipe_path}': {e}")
        return True  # Error occurred while checking the pipe

async def read_pipe(pipe: str, timeout: int=5) -> str:
    if pipe_is_empty(pipe):
        return ""

    try:
        # timeout is not working!
        async with async_timeout.timeout(timeout):
            with open(pipe, 'r', encoding='utf-8') as f:
                data = f.read()
                return data
    except FileNotFoundError:
        print(f"Pipe '{pipe}' does not exist.")
    except PermissionError:
        print(f"No permission to read from pipe '{pipe}'.")
    except asyncio.TimeoutError:
        print("Opening the pipe took too long.")
    except Exception as e:
        if 'Bad file descriptor' in str(e):
            print(f"Pipe '{pipe}' has been closed.")
        else:
            print(f"Error reading from pipe '{pipe}': {e}")

    return ""


def create_pipe(pipe: str):
    try:
        os.mkfifo(pipe)
    except FileExistsError:
        pass


def split_message(message: str, max_length: int = 2000):
    """
    Splits a message into multiple messages with max length of max_length

    Args:
        message (str): Message to split
        max_length (int, optional): Max length of a message. Defaults to 2000.

    Returns:
        list: List of messages
    """
    return [message[i:i+max_length] for i in range(0, len(message), max_length)]
