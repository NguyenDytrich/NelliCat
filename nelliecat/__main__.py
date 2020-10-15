import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

import redis

load_dotenv()
TOKEN = os.getenv("TOKEN")
CLIENT = discord.Client()
REDIS = redis.Redis(host="localhost", port=6379, db=0, charset="utf-8", decode_responses=True)

BOT = commands.Bot(command_prefix="$")


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
        REDIS.set("active", member.id)
        await ctx.send(f"{member.nick} signed in as active consultant.")
    else:
        await ctx.send("Sorry, that command is reserved for consultants!")


@BOT.command(name="active")
async def active(ctx):
    active = REDIS.get("active")
    if active:
        member = await ctx.guild.fetch_member(active)
        await ctx.send(f"{member.nick} is currently in!")
    else:
        await ctx.send(f"No consultant currently signed in at the moment.")


@BOT.command(name="signoff")
async def signoff(ctx):
    active_id = REDIS.get("active")
    active = await ctx.guild.fetch_member(active_id)
    if active == ctx.author:
        REDIS.delete("active")
        await ctx.send(f"Bye {ctx.author.nick}!")


BOT.run(TOKEN)
