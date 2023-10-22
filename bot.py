# By Pytel

import json
import discord
from discord.ext import commands
import random
import socket
import argparse
import subprocess

DEBUG = True
VERBOSE = True

CONFIG_FILE = 'config.json'
API_TOKEN = None
CHANNEL_ID = None
SERVER_ID = None
CATEGORY_ID = None

intents = discord.Intents.default()
intents.message_content = True
description = '''Server controler bot'''
bot = commands.Bot(command_prefix='$',
                   description=description, intents=intents)
guild = discord.Guild

async def create_channel_for_this_pc(server: int, category_id: int = None):
    """
    Creates a new channel for the current PC if it doesn't exist

    Args:
        server (int): ID of the server
    """
    guild = bot.get_guild(server)
    category = guild.get_channel(category_id)
    uname = socket.gethostname()

    text_channel_list = []
    for channel in guild.text_channels:
        text_channel_list.append(channel)

    text_channel_list_names = [channel.name for channel in text_channel_list]

    if DEBUG:
        print('This PC:', uname)
        print('Existing channels:', text_channel_list_names)

    if uname.lower() not in text_channel_list_names:
        if VERBOSE:
            print('Creating new channel:', uname)
        await guild.create_text_channel(uname, category=category)


@bot.event
async def on_ready():
    print('Hello {0.user} !'.format(bot))
    await bot.change_presence(activity=discord.Game('👀'))
    await create_channel_for_this_pc(SERVER_ID, CATEGORY_ID)
    print('------')
    # await sendFromConsole()


@bot.event
async def on_message(message):
    message_content = message.content
    message_author = message.author
    message_channel = message.channel
    # print(message)
    if VERBOSE:
        print(
            f'New message -> {message_author}, in channel: {message_channel}, said: {message_content}')
    await bot.process_commands(message)


@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)


@bot.command()
async def ping(ctx):
    await ctx.send('pong')


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

async def send_message_to_channel(channel_id: int, message: str):
    """
    Sends a message to a channel

    Args:
        channel_id (int): ID of the channel
        message (str): Message to send
    """
    channel = bot.get_channel(channel_id)
    for msg in split_message(message):
        await channel.send(msg)

@bot.command()
async def run(ctx, arg):
    commnad, *args = arg.split(' ')
    print("Running command:", commnad, args)
    output = subprocess.run(
        [commnad, *args],
        capture_output=True
    )
    if VERBOSE:
        print(output)
    
    await send_message_to_channel(ctx.channel.id, output.stdout.decode('utf-8'))


@bot.command()
async def roll(ctx, dice: str):
    """Rolls a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await ctx.send('Format has to be in NdN!')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await ctx.send(result)


@bot.event
async def sendFromConsole():
    run = True
    while run:
        message = input('Enter message: ')
        channel = bot.get_channel(CHANNEL_ID)
        await channel.send(message)


def arg_parser():
    parser = argparse.ArgumentParser(description='Discord bot')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Enable debug mode')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose mode')
    parser.add_argument('-c', '--config', action='store_true', 
                        help='Create new config file')

    args = parser.parse_args()
    # DEBUG = args.debug
    # VERBOSE = args.verbose
    if DEBUG:
        print(args)
    if args.config:
        create_config()
        exit(0)


def create_config(config_file: str = CONFIG_FILE):
    """
    Creates a new config file

    Args:
        config_file (str, optional): Path to config file. Defaults to CONFIG_FILE.
    """
    config = {}
    config['API_TOKEN'] = input('Enter API token: ')
    config['CHANNEL_ID'] = int(input('Enter channel ID: '))
    config['SERVER_ID'] = int(input('Enter server ID: '))
    config['CATEGORY_ID'] = int(input('Enter category ID: '))

    json.dump(config, open(config_file, 'w'), indent=4, sort_keys=True)

def load_config(config_file: str = CONFIG_FILE):
    """
    Loads config file

    Args:
        config_file (str, optional): Path to config file. Defaults to CONFIG_FILE.

    Returns:
        tuple: Tuple containing API_TOKEN, CHANNEL_ID, SERVER_ID, CATEGORY_ID
    """
    config = json.load(open(CONFIG_FILE))
    if DEBUG:
        print(json.dumps(config, indent=4, sort_keys=True))
    return config['API_TOKEN'], config['CHANNEL_ID'], config['SERVER_ID'], config['CATEGORY_ID']

API_TOKEN, CHANNEL_ID, SERVER_ID, CATEGORY_ID = load_config()

if __name__ == "__main__":
    arg_parser()
    
    print(API_TOKEN, CHANNEL_ID, SERVER_ID, CATEGORY_ID)

    bot.run(API_TOKEN)
    
