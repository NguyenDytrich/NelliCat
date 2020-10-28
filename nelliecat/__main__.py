import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

import redis
from dictionary import MwDefinition

load_dotenv()
TOKEN = os.getenv("TOKEN")
REDIS = redis.Redis(
    host="localhost", port=6379, db=0, charset="utf-8", decode_responses=True
)
INTENTS = discord.Intents.default()
INTENTS.members = True

BOT = commands.Bot(command_prefix="$", intents=INTENTS)


def has_role(name, roles):
    role_names = [r.name for r in roles]
    if name in role_names:
        return True
    else:
        return False


def get_channel(name, channels):
    channel = None
    for c in channels:
        if name == c.name:
            channel = c
            break
    return channel


class Greeting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        welcome = get_channel("welcome", member.guild.text_channels)
        resources = get_channel("resources", member.guild.text_channels)
        if welcome:
            # TODO: format this string
            string = (
                f"Hey {member.mention}, welcome to the {member.guild.name}! If you"
                "have any questions, please ask a consultant in #questions. Depending"
                "on who's on the clock, and if it's business hours, we'll get back to"
                "you right away!\n\n"
                "If you'd like to schedule a synchronous meeting (Zoom), or"
                f"asynchronous feedback (video feedback), check out the {resources.mention} channel."
            )

            await welcome.send(string)


class Dictionary(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def define(self, ctx, arg):
        definition = MwDefinition(arg)
        await ctx.send(embed=definition.get_embed())


@BOT.command(name="signin")
async def signin(ctx):
    member = ctx.author
    if has_role("Consultant", member.roles):
        REDIS.set("active", member.id)
        await ctx.send(f"{member.display_name} signed in as active consultant.")
    else:
        await ctx.send("Sorry, that command is reserved for consultants!")


@BOT.command(name="active")
async def active(ctx):
    active = REDIS.get("active")
    if active:
        member = await ctx.guild.fetch_member(active)
        await ctx.send(f"{member.display_name} is currently in!")
    else:
        await ctx.send(f"No consultant currently signed in at the moment.")


@BOT.command(name="signoff")
async def signoff(ctx):
    active_id = REDIS.get("active")
    active = await ctx.guild.fetch_member(active_id)
    if active == ctx.author:
        REDIS.delete("active")
        await ctx.send(f"Bye {ctx.author.display_name}!")


@BOT.event
async def on_ready():
    print("Nelliecat bot live and ready")


BOT.add_cog(Greeting(BOT))
BOT.add_cog(Dictionary(BOT))
BOT.run(TOKEN)
