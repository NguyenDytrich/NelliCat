import os

import discord
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv("TOKEN")
CLIENT = discord.Client()

BOT = commands.Bot(command_prefix="$")

ACTIVE_CONSULTANT = None


def has_role(name, roles):
    role_names = [r.name for r in roles]
    if name in role_names:
        return True
    else:
        return False


@BOT.command(name="signin")
async def signin(ctx):
    member = ctx.author
    if has_role("Consultant", member.roles):
        global ACTIVE_CONSULTANT
        ACTIVE_CONSULTANT = member
        await ctx.send(f"{member.nick} signed in as active consultant.")
    else:
        await ctx.send("Sorry, that command is reserved for consultants!")


@BOT.command(name="active")
async def active(ctx):
    if ACTIVE_CONSULTANT:
        await ctx.send(f"{ACTIVE_CONSULTANT.nick} is currently in!")
    else:
        await ctx.send(f"No consultant currently signed in at the moment.")

@BOT.command(name="signoff")
async def signoff(ctx):
    global  ACTIVE_CONSULTANT
    if ACTIVE_CONSULTANT == ctx.author:
        ACTIVE_CONSULTANT = None
        await ctx.send(f"Bye {ctx.author.nick}!")


BOT.run(TOKEN)
