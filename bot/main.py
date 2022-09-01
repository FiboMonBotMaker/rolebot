from discord.ext import commands
import os
import pathlib
import discord
from lib.dbutil import create_talbe, primary_key
from lib.locale import get_lang


# DataBaseの初期化 既にテーブルが存在している場合は作成しない
create_talbe(
    table_name="roles",
    columns=[
        "guild_id bigint",
        "role_id bigint",
        "INDEX guids_index(guild_id)",
        primary_key(["guild_id", "role_id"])
    ]
)

create_talbe(
    table_name="panels",
    columns=[
        "guild_id bigint",
        "channel_id bigint NOT NULL",
        "message_id bigint NOT NULL",
        primary_key(["guild_id"])
    ]
)

create_talbe(
    table_name="threads",
    columns=[
        "guild_id bigint",
        "thread_id bigint",
        "webhook_id bigint NOT NULL",
        primary_key(["guild_id", "thread_id"])
    ]
)


intent = discord.Intents.default()
intent.guilds = True
intent.members = True
intent.messages = True

bot = commands.Bot(
    debug_guilds=os.getenv("GUILDS").split(","),
    intent=intent
)
TOKEN = os.getenv('TOKEN')

path = "./cogs"


@bot.event
async def on_ready():
    print(f"Bot名:{bot.user} On ready!!")


@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext, error: Exception):
    lang = get_lang(ctx.locale)
    if isinstance(error, commands.MissingPermissions):
        await ctx.respond(lang["error"]["admincommand"], ephemeral=True)
    else:
        raise error


# @bot.event
# async def on_message(message: discord.Message):
#     if message.channel.id in threads[message.guild.id]:


dir = "cogs"
files = pathlib.Path(dir).glob("*.py")
for file in files:
    print(f"{dir}.{file.name[:-3]}")
    bot.load_extension(name=f"{dir}.{file.name[:-3]}", store=False)


bot.run(TOKEN)
