# By Pytel

import random
import socket
import subprocess
import discord
from discord.ext import commands, tasks
from tools import *

DEBUG = True
VERBOSE = True

CONFIG_FILE = 'config.json'
PIPE_PATH = '/dev/shm/discord_pipe'
PIPE_PATH = 'discord_pipe'

ERROR = '❌'
SUCCESS = '✅'
WARNING = '⚠️'
INFO = 'ℹ️'


class MyBot(commands.Bot):
    COMMAND_PREFIX = '$'
    CHANNEL_ID = None
    PIPE_READING_PERIOD_S = 10

    intents = discord.Intents.default()
    intents.message_content = True
    description = '''Server controler bot'''

    def __str__(self):
        text = str(
            " - API_TOKEN: \n" + self.API_TOKEN + "\n" + 
            " - SERVER_ID: \t" + str(self.SERVER_ID) + "\n" + 
            " - CATEGORY_ID: " + str(self.CATEGORY_ID) + "\n" + 
            " - CHANNEL_ID: " + str(self.CHANNEL_ID) + "\n" +
            " - COMMAND_PREFIX: " + self.COMMAND_PREFIX + "\n" + 
            " - PIPE_READING_PERIOD_S: " + str(self.PIPE_READING_PERIOD_S) + "\n" + 
            " - description: " + self.description + "\n" + 
            " - args: " + str(self.args))
        
        return text

    def __init__(self, args, command_prefix=COMMAND_PREFIX, self_bot=False):
        if args.config:
            create_config(CONFIG_FILE)
            exit(0)

        super().__init__(command_prefix=command_prefix,
                         description=self.description, intents=self.intents, self_bot=self_bot)
        self.args = args
        self.API_TOKEN, self.SERVER_ID, self.CATEGORY_ID = load_config(
            CONFIG_FILE)
        self.add_commands()
        if DEBUG:
            print(self)

    async def on_ready(self):
        print('Hello {0.user} !'.format(self))
        await self.change_presence(activity=discord.Game('👀'))
        await self.create_channel_for_this_pc(self.SERVER_ID, self.CATEGORY_ID)

        if self.args.pipe:
            # create_pipe(PIPE_PATH)
            if VERBOSE:
                print('Starting pipe reading task...')
            self.send_message_from_pipe.start()
        print('------')

    async def on_message(self, message):
        # print(message)
        if VERBOSE:
            print(
                f'New message -> {message.author}, in channel: {message.channel}, said: {message.content}')

        # test for right server
        if message.guild.id != self.SERVER_ID:
            if VERBOSE:
                print(WARNING, 'Wrong server: {0.guild.id}'.format(message))
            return

        # test for right category
        if message.channel.category_id != self.CATEGORY_ID:
            if VERBOSE:
                print(
                    INFO, 'Wrong category: {0.channel.category_id}'.format(message))
            return

        # test for right channel
        if message.channel.id != self.CHANNEL_ID:
            if VERBOSE:
                print(INFO, 'Wrong channel: {0.channel.id}'.format(message))
            return

        # if its bot do nothing
        if message.author == self.user:
            if VERBOSE:
                print(INFO, 'Bot message')
            return

        if DEBUG:
            print('Executing command...')
        await self.process_commands(message)

    def get_channel_id(self, channel_name: str, server_id: int) -> int:
        """
        Gets channel ID from channel name

        Args:
            channel_name (str): Name of the channel
            server_id (int): ID of the server

        Returns:
            int: ID of the channel
        """
        guild = self.get_guild(server_id)
        for channel in guild.text_channels:
            if channel.name == channel_name:
                return channel.id
        return None

    async def create_channel_for_this_pc(self, server: int, category_id: int = None):
        """
        Creates a new channel for the current PC if it doesn't exist

        Args:
            server (int): ID of the server
        """
        guild = self.get_guild(server)
        category = guild.get_channel(category_id)
        uname = socket.gethostname().lower()

        text_channel_list = []
        for channel in guild.text_channels:
            text_channel_list.append(channel)

        text_channel_list_names = [
            channel.name for channel in text_channel_list]

        if DEBUG:
            print('This PC:', uname)
            print('Existing channels:', text_channel_list_names)

        if uname not in text_channel_list_names:
            if VERBOSE:
                print('Creating new channel:', uname)
            await guild.create_text_channel(uname, category=category)

        
        self.CHANNEL_ID = self.get_channel_id(uname, server)
        if VERBOSE:
            print('Setting channel ID to:', self.CHANNEL_ID)

        if self.CHANNEL_ID is None:
            print("Channel: {0} not in server: {1}".format(uname, server))
            for channel in guild.text_channels:
                print(channel.name)
            raise Exception(
                'Channel ID is None, unable to verify if channel was created!')

    async def send_message_to_channel(channel_id: int, message: str):
        """
        Sends a message to a channel

        Args:
            channel_id (int): ID of the channel
            message (str): Message to send
        """
        channel = MyBot.get_channel(channel_id)
        for msg in split_message(message):
            await channel.send(msg)

    def add_commands(self):

        @self.command()
        async def test(ctx, arg):
            if DEBUG:
                print('Test command:', arg)
            await ctx.send(arg)

        @self.command()
        async def ping(ctx):
            await ctx.send('pong')

        @self.command()
        async def run(ctx, arg):
            commnad, *args = arg.split(' ')
            print("Running command:", commnad, args)
            output = subprocess.run(
                [commnad, *args],
                capture_output=True
            )
            if VERBOSE:
                print(output)

            await MyBot.send_message_to_channel(ctx.channel.id, output.stdout.decode('utf-8'))

        @self.command()
        async def file(ctx, arg):
            """
            Sends a file to a channel.
            """
            file_name = arg.split('/')[-1]
            file_path = arg
            # do file exist?
            if not os.path.isfile(file_path):
                await ctx.send('File does not exist!')
                return
            # is file too big?
            if os.path.getsize(file_path) > 8 * 1024 * 1024:
                await ctx.send('File is too big!')
                return
            # send file
            await ctx.send(file=discord.File(file_path, filename=file_name))

        @self.command()
        async def roll(ctx, dice: str):
            """Rolls a dice in NdN format."""
            try:
                rolls, limit = map(int, dice.split('d'))
            except Exception:
                await ctx.send('Format has to be in NdN!')
                return

            result = ', '.join(str(random.randint(1, limit))
                               for r in range(rolls))
            await ctx.send(result)

    @tasks.loop(seconds=PIPE_READING_PERIOD_S)
    async def send_message_from_pipe(self):
        """
        Sends a message from a pipe to a channel in interval of PIPE_READING_PERIOD_S seconds
        """
        message = await read_pipe(PIPE_PATH)
        print(str(self.CHANNEL_ID) + " " + message)
        if message:            
            await MyBot.send_message_to_channel(self.CHANNEL_ID, message)
            if DEBUG:
                print(f"Opened pipe successfully: {message}")
        elif DEBUG:
            print('No message in pipe...')
