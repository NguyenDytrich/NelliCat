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


async def send_rules(channel):
    embed = discord.Embed(title="Rules")
    embed.add_field(inline=False, name="\u200B", value="1. Be polite")
    embed.add_field(inline=False, name="\u200B", value="2. Don't eat ALL the cookies")
    embed.add_field(
        inline=False,
        name="\u200B",
        value=(
            "3. Please make yourself aware of fire exits A and B to the"
            "front and left of the room"
        ),
    )
    embed.add_field(
        inline=False,
        name="\u200B",
        value="After reading, please gives this message a :thumbsup: reaction!",
    )
    msg = await channel.send(embed=embed)
    REDIS.set("rules_msg_id", msg.id)


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
        rules = get_channel("rules", member.guild.text_channels)

        if welcome:
            embed = discord.Embed()

            embed.set_image(url=os.getenv("WELCOME_IMAGE_URL"))

            string = (
                f"Hey {member.mention}, welcome to the **{member.guild.name}**!\n\n"
                f"First of all, please read the rules in {rules.mention}!\n\n"
                "If you'd like to schedule a synchronous meeting (Zoom), or "
                f"asynchronous feedback (video feedback), check out the {resources.mention} channel.\n\n"
                f"Use the $active command in {bot_channel.mention} to see who's currently in! "
                f"If you have any questions, please ask a consultant in {questions.mention}. Depending "
                "on if it's business hours, and if anyone is in, we'll get back to you as soon as possible.\n\n"
                f"Otherwise feel free to hang out in {general.mention} as long as you'd like!"
            )

            embed.add_field(name="Welcome", value=string)

            await welcome.send(embed=embed)

        if not REDIS.get("rules_msg_id"):
            embed = discord.Embed(title="Rules")
            embed.add_field(inline=False, name="\u200B", value="1. Be polite")
            embed.add_field(
                inline=False, name="\u200B", value="2. Don't eat ALL the cookies"
            )
            embed.add_field(
                inline=False,
                name="\u200B",
                value="3. Please make yourself aware of fire exits A and B to the front and left of the room",
            )
            embed.add_field(
                inline=False,
                name="\u200B",
                value="After reading, please gives this message a :thumbsup: reaction!",
            )

            send_rules(rules)


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


@BOT.command(name="rules")
async def rules(ctx):
    rules = get_channel("rules", ctx.author.guild.text_channels)
    rules_msg_id = REDIS.get("rules_msg_id")
    try:
        if rules_msg_id:
            last_msg = await rules.fetch_message(rules_msg_id)
            if rules.last_message_id:
                await ctx.send(f"Rules are posted on {rules.mention}")
        else:
            await send_rules(rules)
    except discord.NotFound:
        await send_rules(rules)


@BOT.event
async def on_ready():
    print("Nelliecat bot live and ready")


@BOT.listen("on_raw_reaction_add")
async def check_rules_reaction(reaction):
    writer_role = [r for r in reaction.member.guild.roles if r.name == "Writer"]
    rules_msg_id = REDIS.get("rules_msg_id")
    is_thumbsup = reaction.emoji.name == "👍"
    is_rules_react = reaction.message_id == int(rules_msg_id)

    print(reaction.emoji)

    if is_rules_react and is_thumbsup:
        print(writer_role[0])
        await reaction.member.add_roles(writer_role[0])

BOT.add_cog(Greeting(BOT))
BOT.add_cog(Dictionary(BOT))
BOT.run(TOKEN)
