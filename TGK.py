# Standard libraries
import contextlib
import io
import logging
import os
from dotenv import load_dotenv

# Third party libraries
import textwrap
import datetime
import discord
import json
import motor.motor_asyncio

from traceback import format_exception

from discord.ext import commands
from pathlib import Path
from better_help import Help

# Local code
import utils.json_loader

from utils.mongo import Document
from utils.util import Pag
from utils.util import clean_code

load_dotenv()
cwd = Path(__file__).parents[0]
cwd = str(cwd)
print(f"{cwd}\n-----")


async def get_prefix(bot, message):
    # If dm's
    if not message.guild:
        return commands.when_mentioned_or(bot.DEFAULTPREFIX)(bot, message)

    try:
        data = await bot.config.find(message.guild.id)

        # Make sure we have a useable prefix
        if not data or "prefix" not in data:
            return commands.when_mentioned_or(bot.DEFAULTPREFIX)(bot, message)
        return commands.when_mentioned_or(data["prefix"])(bot, message)
    except:
        return commands.when_mentioned_or(bot.DEFAULTPREFIX)(bot, message)


intents = discord.Intents.all()  # Help command requires member intents
DEFAULTPREFIX = "!"
bot = commands.Bot(
    description="commands List of Me",
    command_prefix=get_prefix,
    case_insensitive=True,
    owner_ids=[391913988461559809, 488614633670967307, 301657045248114690],
    help_command=Help(ending_note=f"Made By Jay and Utki", show_cooldown=False,
                      show_brief=True, timeout=60, timeout_delete=True),
    intents=intents,
)
# change command_prefix='-' to command_prefix=get_prefix for custom prefixes
bot.config_token = os.getenv('TOKEN')
bot.connection_url = str(os.getenv('MONGO'))
bot.joke_api_key = os.getenv('DAD')

logging.basicConfig(level=logging.INFO)

bot.DEFAULTPREFIX = DEFAULTPREFIX
bot.muted_users = {}
bot.ban_users = {}
bot.blacklist_user = {}
bot.guild_id = [797920317871357972]
bot.ticket_setups = {}
bot.cwd = cwd
bot.event_channel = {}
bot.perm = {}
bot.afk_user = {}
bot.free_users = {}
bot.giveaway = {}
bot.mod_role = [797923152617275433, 848585998769455104]
bot.version = "4.1"
bot.uptime = datetime.datetime.utcnow()

bot.colors = {
    "WHITE": 0xFFFFFF,
    "AQUA": 0x1ABC9C,
    "GREEN": 0x2ECC71,
    "BLUE": 0x3498DB,
    "PURPLE": 0x9B59B6,
    "LUMINOUS_VIVID_PINK": 0xE91E63,
    "GOLD": 0xF1C40F,
    "ORANGE": 0xE67E22,
    "RED": 0xE74C3C,
    "NAVY": 0x34495E,
    "DARK_AQUA": 0x11806A,
    "DARK_GREEN": 0x1F8B4C,
    "DARK_BLUE": 0x206694,
    "DARK_PURPLE": 0x71368A,
    "DARK_VIVID_PINK": 0xAD1457,
    "DARK_GOLD": 0xC27C0E,
    "DARK_ORANGE": 0xA84300,
    "DARK_RED": 0x992D22,
    "DARK_NAVY": 0x2C3E50,
}
bot.color_list = [c for c in bot.colors.values()]


@bot.event
async def on_ready():
    # On ready, print some details to standard out
    print(
        f"-----\nLogged in as: {bot.user.name} : {bot.user.id}\n-----\nMy current prefix is: {bot.DEFAULTPREFIX}\n-----"
    )
    await bot.change_presence(status=discord.Status.dnd)

    print("jishaku has been loaded\n-----")

    current_blacklist_user = await bot.blacklist.get_all()
    for blacklisted_user in current_blacklist_user:
        bot.blacklist_user[blacklisted_user["_id"]] = blacklisted_user

    currentMutes = await bot.mutes.get_all()
    for mute in currentMutes:
        bot.muted_users[mute["_id"]] = mute

    currentBans = await bot.bans.get_all()
    for ban in currentBans:
        bot.ban_users[ban["_id"]] = ban

    current_afk_user = await bot.afk.get_all()
    for afk in current_afk_user:
        bot.afk_user[afk["_id"]] = afk

    currentFree = await bot.free.get_all()
    for free in currentFree:
        bot.free_users[free["_id"]] = free

    currentGive = await bot.give.get_all()
    for give in currentGive:
        bot.giveaway[give["_id"]] = give

    datas = await bot.ticket_setup.get_all()
    for data in datas:
        setup = json.dumps(data)
        bot.ticket_setups = json.loads(setup)

    try:
        permissions = await bot.perms.get_all()
        permission = json.dumps(permissions)
        bot.perm = json.loads(permission)
    except:
        pass

    try:
        channels = await bot.event.get_all()
        channel = json.dumps(channels[0]["event_channels"])
        bot.event_channel = json.loads(channel)
    except:
        pass

    print("\n-----")
    print(f"Current blacklist:{len(bot.blacklist_user)}")
    print("\n-----")
    print(f"Current Mutes:{len(bot.muted_users)}")
    print("\n-----")
    print(f"Current Bans:{len(bot.ban_users)}")
    print("\n-----")
    print(f"Current Free users:{len(bot.free_users)}")
    print(f"Current giveaway:{len(bot.giveaway)}")
    print("\n-----")
    print("Database Connected\n-----")


@bot.event
async def on_message(message):
    # Ignore messages sent by yourself
    if message.author.bot:
        return

    # A way to blacklist users from the bot by not processing commands
    # if the author is in the blacklisted list
    if message.author.id in bot.blacklist_user:
        return

    # Whenever the bot is tagged, respond with its prefix
    if message.content.startswith(f"<@!{bot.user.id}>") and len(message.content) == len(
        f"<@!{bot.user.id}>"
    ):
        data = await bot.config.find_by_id(message.guild.id)
        if not data or "prefix" not in data:
            prefix = bot.DEFAULTPREFIX
        else:
            prefix = data["prefix"]
        await message.channel.send(f"My prefix here is `{prefix}`", delete_after=15)

    await bot.process_commands(message)


if __name__ == "__main__":
    # When running this file, if it is the 'main' file
    # I.E its not being imported from another python file run this
    bot.mongo = motor.motor_asyncio.AsyncIOMotorClient(str(bot.connection_url))
    bot.db = bot.mongo["tgk_database"]
    bot.config = Document(bot.db, "config")
    bot.afk = Document(bot.db, "afk")
    bot.mutes = Document(bot.db, "mutes")
    bot.bans = Document(bot.db, "bans")
    bot.warns = Document(bot.db, "warns")
    bot.ticket = Document(bot.db, "ticket")
    bot.ticket_setup = Document(bot.db, "ticket_setup")
    bot.blacklist = Document(bot.db, "blacklist")
    bot.invites = Document(bot.db, "invites")
    bot.tasks = Document(bot.db, "tasks")
    bot.lockdown = Document(bot.db, "lockdown")
    bot.event = Document(bot.db, "event")
    bot.score = Document(bot.db, "score")
    bot.embed = Document(bot.db, "embed")
    bot.casino = Document(bot.db, "casino")
    bot.free = Document(bot.db, "free")
    bot.give = Document(bot.db, "give")

    for file in os.listdir(cwd + "/cogs"):
        if file.endswith(".py") and not file.startswith("_") and not file.startswith("test") and not file.startswith("events"):
            bot.load_extension(f"cogs.{file[:-3]}")

    bot.run(bot.config_token)

"""

{
    "token": "ODMxNTYzNzgwNTI5MzI0MDMy.YHXEHg.7cm20TLRjhmXFmxl4KwUbwQIGWc",
    "mongo": "mongodb+srv://test121:test121@cluster0.l4ljr.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",
    "x-rapidapi-key": "61081de6d7msh9b9cc262fb7993dp1ed8f8jsn4d6720e23330"
}
"""
