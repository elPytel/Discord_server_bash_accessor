# pip install discord.py

import discord
from discord.ext import commands
import random

CONFIG_FILE = 'api_token.conf'

intents = discord.Intents.default()
intents.message_content = True
description = '''My first Discord bot'''
bot = commands.Bot(command_prefix='?', description=description, intents=intents)
guild = discord.Guild


@bot.event
async def on_ready():
    print('Hello {0.user} !'.format(bot))
    await bot.change_presence(activity=discord.Game('👀'))


@bot.event
async def on_message(message):
    message_content = message.content
    message_author = message.author
    print(f'New message -> {message_author} said: {message_content}')
    await bot.process_commands(message)

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


if __name__ == "__main__":
    with open(CONFIG_FILE, 'r') as f:
        API_TOKEN = f.readline().strip()
    bot.run(API_TOKEN)