import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

from db import models, operations
from commands import request_commands, trade_commands, info_commands

# Load the environment variables from the .env file
load_dotenv()

# Get the bot token from the environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Create an instance of discord.Intents
intents = discord.Intents.default()

# Allow the bot to receive certain types of events
intents.messages = True
intents.reactions = True
intents.guilds = True
intents.message_content = True

# Create an instance of the bot
bot = commands.Bot(command_prefix="!", intents=intents)

request_commands.setup(bot)
trade_commands.setup(bot)
info_commands.setup(bot)

# Event handler for when the bot is ready
@bot.event
async def on_ready():
    # Print out the bot's name and id when it's ready
    print(f"Logged in as {bot.user.name} - {bot.user.id}")


bot.run(BOT_TOKEN)

