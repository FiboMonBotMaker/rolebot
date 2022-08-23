from discord.ext import commands
import os
import pathlib
import discord
from lib.dbutil import create_talbe, primary_key


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


intent = discord.Intents.all()
bot = commands.Bot(debug_guilds=[os.getenv(
    'GUILD'), os.getenv('GUILD2')], intent=intent)
TOKEN = os.getenv('TOKEN')

path = "./cogs"


@bot.event
async def on_ready():
    print(f"Bot名:{bot.user} On ready!!")


@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext, error: Exception):
    if isinstance(error, commands.MissingPermissions):
        await ctx.respond("This command is for administrators only !!", ephemeral=True)
    else:
        raise error

dir = "cogs"
files = pathlib.Path(dir).glob("*.py")
for file in files:
    print(f"{dir}.{file.name[:-3]}")
    bot.load_extension(name=f"{dir}.{file.name[:-3]}", store=False)


bot.run(TOKEN)
