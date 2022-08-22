from discord.ext import commands
import os
import pathlib
import discord

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
        await ctx.respond(error, ephemeral=True)
    else:
        raise error

dir = "cogs"
files = pathlib.Path(dir).glob("*.py")
for file in files:
    print(f"{dir}.{file.name[:-3]}")
    bot.load_extension(name=f"{dir}.{file.name[:-3]}", store=False)


bot.run(TOKEN)
