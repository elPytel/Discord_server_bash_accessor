# By Pytel

import os

def read_pipe(pipe: str) -> str:
    with open(pipe, 'r', encoding='utf-8') as f:
        return f.read()


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
