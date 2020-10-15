import os

import discord
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv("TOKEN")
CLIENT = discord.Client()


@CLIENT.event
async def on_ready():
    """Let us know that the bot is combat ready"""
    print("NellieCat online and ready")

CLIENT.run(TOKEN)
