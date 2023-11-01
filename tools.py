# By Pytel

import os
import json
import asyncio
import async_timeout

def create_config(config_file: str):
    """
    Creates a new config file

    Args:
        config_file (str, optional): Path to config file.
    """
    config = {}
    config['API_TOKEN'] = input('Enter API token: ')
    config['SERVER_ID'] = int(input('Enter server ID: '))
    config['CATEGORY_ID'] = int(input('Enter category ID: '))

    json.dump(config, open(config_file, 'w', encoding='utf-8'),
              indent=4, sort_keys=True)


def load_config(config_file: str) -> tuple:
    """
    Loads config file

    Args:
        config_file (str, optional): Path to config file.

    Returns:
        tuple: Tuple containing API_TOKEN, CHANNEL_ID, SERVER_ID, CATEGORY_ID
    """
    config = json.load(open(config_file, 'r', encoding='utf-8'))
    #print(json.dumps(config, indent=4, sort_keys=True))
    return config['API_TOKEN'], config['SERVER_ID'], config['CATEGORY_ID']


def pipe_is_empty(pipe_path: str) -> bool:
    """
    Checks if a named pipe size is 0.
    If the pipe does not exist, it returns True.

    Args:
        pipe_path (str): Path to the pipe

    Returns:
        bool: True if pipe is empty or does not exist, False otherwise
    """
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
    """
    Reads text from a named pipe.
    Automatically tests if the pipe is empty.

    Args:
        pipe (str): Path to the pipe
        timeout (int, optional): Timeout in seconds. Defaults to 5.

    Returns:
        str: Data from the pipe or empty string if pipe is empty
    """
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
