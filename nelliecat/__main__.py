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
        # TODO this is probably a bad way of getting the channels
        welcome = get_channel("welcome", member.guild.text_channels)
        resources = get_channel("resources", member.guild.text_channels)
        bot_channel = get_channel("bot-channel", member.guild.text_channels)
        questions = get_channel("questions", member.guild.text_channels)
        general = get_channel("general", member.guild.text_channels)

        if welcome:
            embed = discord.Embed()

            embed.set_image(url=os.getenv("WELCOME_IMAGE_URL"))

            string = (
                f"Hey {member.mention}, welcome to the **{member.guild.name}**!\n\n"
                "If you'd like to schedule a synchronous meeting (Zoom), or "
                f"asynchronous feedback (video feedback), check out the {resources.mention} channel.\n\n"
                f"Use the $active command in {bot_channel.mention} to see who's currently in! "
                f"If you have any questions, please ask a consultant in {questions.mention}. Depending "
                "on if it's business hours, and if anyone is in, we'll get back to you as soon as possible.\n\n"
                f"Otherwise feel free to hang out in {general.mention} as long as you'd like!"
            )

            embed.add_field(name="Welcome", value=string)

            await welcome.send(embed=embed)


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
